"""Reproducible portfolio segmentation and leakage-aware baseline model evaluation."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (roc_auc_score, average_precision_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report, balanced_accuracy_score, brier_score_loss, accuracy_score)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.validate_data import validate_dataframe

NUMERIC = ["loan_amnt", "annual_inc", "dti", "int_rate", "term_months", "delinq_2yrs"]
CATEGORICAL = ["grade", "emp_length", "home_ownership", "purpose"]
FEATURES = NUMERIC + CATEGORICAL  # Excludes ids, dates, status, target and post-origination outcomes.

def add_bands(df: pd.DataFrame) -> pd.DataFrame:
    x = df.copy()
    x["income_band"] = pd.cut(pd.to_numeric(x["annual_inc"], errors="coerce"),
        bins=[-np.inf, 25_000, 50_000, 75_000, 100_000, np.inf],
        labels=["<$25k", "$25k–$50k", "$50k–$75k", "$75k–$100k", "$100k+"], right=False).astype("object").fillna("Unknown")
    x["dti_band"] = pd.cut(pd.to_numeric(x["dti"], errors="coerce"),
        bins=[-np.inf, 10, 20, 25, 35, np.inf], labels=["<10", "10–<20", "20–<25", "25–<35", "35+"], right=False).astype("object").fillna("Unknown")
    return x

def _wilson_interval(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0: return (float("nan"), float("nan"))
    p = successes / n; denom = 1 + z*z/n
    center = (p + z*z/(2*n)) / denom
    half = z * np.sqrt((p*(1-p) + z*z/(4*n))/n) / denom
    return max(0.0, center-half)*100, min(1.0, center+half)*100

def segment_table(df: pd.DataFrame, key: str) -> pd.DataFrame:
    g = df.groupby(key, dropna=False, observed=False).agg(
        loans=("loan_id", "count"), defaults=("default_flag", "sum"),
        default_rate=("default_flag", "mean"), avg_loan_amount=("loan_amnt", "mean"),
    ).reset_index()
    intervals = [_wilson_interval(int(d), int(n)) for d,n in zip(g.defaults, g.loans)]
    g["default_rate_pct"] = g["default_rate"] * 100
    g["ci_95_low_pct"] = [v[0] for v in intervals]
    g["ci_95_high_pct"] = [v[1] for v in intervals]
    g["avg_loan_amount"] = g["avg_loan_amount"].round(2)
    return g.drop(columns="default_rate").sort_values("loans", ascending=False).reset_index(drop=True)

def _metric_pack(y_true, probabilities, threshold=0.5) -> dict:
    pred = (probabilities >= threshold).astype(int)
    return {
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "average_precision": float(average_precision_score(y_true, probabilities)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, pred)),
        "precision_default": float(precision_score(y_true, pred, zero_division=0)),
        "recall_default": float(recall_score(y_true, pred, zero_division=0)),
        "f1_default": float(f1_score(y_true, pred, zero_division=0)),
        "brier_score": float(brier_score_loss(y_true, probabilities)),
        "threshold": float(threshold),
        "confusion_matrix": confusion_matrix(y_true, pred, labels=[0,1]).tolist(),
        "classification_report": classification_report(y_true, pred, labels=[0,1], target_names=["non_default", "default"], output_dict=True, zero_division=0),
    }

def _make_split(data: pd.DataFrame, y: pd.Series):
    dates = pd.to_datetime(data["issue_date"], errors="coerce")
    train_cutoff = dates.quantile(0.70)
    validation_cutoff = dates.quantile(0.85)
    train_idx = np.flatnonzero((dates < train_cutoff).to_numpy())
    validation_idx = np.flatnonzero(((dates >= train_cutoff) & (dates < validation_cutoff)).to_numpy())
    test_idx = np.flatnonzero((dates >= validation_cutoff).to_numpy())
    parts = [train_idx, validation_idx, test_idx]
    if all(len(part) >= 50 and y.iloc[part].nunique() == 2 for part in parts):
        return train_idx, validation_idx, test_idx, "out_of_time_70_15_15", str(pd.Timestamp(train_cutoff).date()), str(pd.Timestamp(validation_cutoff).date())
    # Fallback is explicit and only used for small/date-concentrated external files.
    all_idx = np.arange(len(data))
    train_validation_idx, test_idx = train_test_split(all_idx, test_size=0.20, random_state=42, stratify=y)
    train_idx, validation_idx = train_test_split(train_validation_idx, test_size=0.1875, random_state=42, stratify=y.iloc[train_validation_idx])
    return np.asarray(train_idx), np.asarray(validation_idx), np.asarray(test_idx), "stratified_random_fallback", None, None

def _select_threshold(y_true, probabilities) -> tuple[float, float]:
    """Choose a demonstrative F1 threshold on validation data only, never on test data."""
    candidates = np.round(np.arange(0.05, 0.501, 0.01), 2)
    scored = [(float(f1_score(y_true, probabilities >= t, zero_division=0)), float(t)) for t in candidates]
    best_f1 = max(score for score, _ in scored)
    best_threshold = max(t for score, t in scored if score == best_f1)  # tie-break toward fewer flagged records
    return best_threshold, float(best_f1)

def run_analysis(df: pd.DataFrame) -> dict:
    quality = validate_dataframe(df)
    if not quality["passed"]: raise ValueError("Data quality checks failed: " + ", ".join(quality["problems"]))
    data = add_bands(df)
    data["issue_date"] = pd.to_datetime(data["issue_date"], errors="coerce")
    target = pd.to_numeric(data["default_flag"]).astype(int).reset_index(drop=True)
    data = data.reset_index(drop=True)
    if target.nunique() < 2: raise ValueError("Target must contain both 0 and 1 classes")
    train_idx, validation_idx, test_idx, split_method, train_cutoff, validation_cutoff = _make_split(data, target)
    X = data[FEATURES].copy(); y = target
    numeric_transform = Pipeline([("imputer", SimpleImputer(strategy="median", add_indicator=True)), ("scaler", StandardScaler())])
    categorical_transform = Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))])
    preprocessor = ColumnTransformer([("num", numeric_transform, NUMERIC), ("cat", categorical_transform, CATEGORICAL)])
    # Plain logistic regression gives a more interpretable baseline probability scale than reweighting classes.
    model = Pipeline([("preprocess", preprocessor), ("classifier", LogisticRegression(max_iter=1500, random_state=42))])
    dummy = Pipeline([("preprocess", preprocessor), ("classifier", DummyClassifier(strategy="prior"))])
    model.fit(X.iloc[train_idx], y.iloc[train_idx])
    dummy.fit(X.iloc[train_idx], y.iloc[train_idx])
    validation_prob = model.predict_proba(X.iloc[validation_idx])[:,1]
    selected_threshold, validation_f1 = _select_threshold(y.iloc[validation_idx].to_numpy(), validation_prob)
    probabilities = model.predict_proba(X.iloc[test_idx])[:,1]
    baseline_prob = dummy.predict_proba(X.iloc[test_idx])[:,1]
    metrics = _metric_pack(y.iloc[test_idx].to_numpy(), probabilities, threshold=selected_threshold)
    baseline_metrics = _metric_pack(y.iloc[test_idx].to_numpy(), baseline_prob, threshold=selected_threshold)
    metrics.update({
        "rows": int(len(data)), "defaults": int(y.sum()), "default_rate_pct": round(float(y.mean()*100), 2),
        "train_rows": int(len(train_idx)), "validation_rows": int(len(validation_idx)), "test_rows": int(len(test_idx)),
        "split_method": split_method, "train_cutoff": train_cutoff, "validation_cutoff": validation_cutoff,
        "test_start_date": str(data.iloc[test_idx]["issue_date"].min().date()),
        "validation_selected_threshold_f1": selected_threshold, "validation_f1_at_selected_threshold": validation_f1,
        "baseline_roc_auc": baseline_metrics["roc_auc"], "baseline_average_precision": baseline_metrics["average_precision"],
        "baseline_brier_score": baseline_metrics["brier_score"],
    })
    segment_output = {
        "grade_segments": segment_table(data, "grade"), "income_segments": segment_table(data, "income_band"),
        "term_segments": segment_table(data, "term_months"), "dti_segments": segment_table(data, "dti_band"),
        "purpose_segments": segment_table(data, "purpose"),
    }
    subset = data[data["grade"].astype(str).isin(["D", "E"]) & (data["dti"] > 25)]
    target_segment = {"segment":"Grades D/E and DTI > 25", "loans":int(len(subset)), "defaults":int(subset["default_flag"].sum()) if len(subset) else 0,
        "default_rate_pct":round(float(subset["default_flag"].mean()*100),2) if len(subset) else None,
        "status":"synthetic demo calculation; verify on source data before citing as a finding"}
    predictions = data.iloc[test_idx][["loan_id", "issue_date", "grade", "dti", "default_flag"]].copy()
    predictions["predicted_default_probability"] = probabilities
    predictions["predicted_default_at_validation_threshold"] = (probabilities >= selected_threshold).astype(int)
    predictions["model_test_set"] = split_method
    return {"metrics":metrics, "baseline_metrics":baseline_metrics, "quality":quality,
        **segment_output, "grade_de_target":target_segment, "predictions":predictions, "model":model}

def write_outputs(result: dict, output_dir: str | Path) -> None:
    out=Path(output_dir); out.mkdir(parents=True, exist_ok=True)
    serializable={k:v for k,v in result["metrics"].items() if k != "classification_report"}
    serializable["classification_report"] = result["metrics"]["classification_report"]
    (out/"model_metrics.json").write_text(json.dumps(serializable, indent=2, default=float))
    (out/"baseline_metrics.json").write_text(json.dumps(result["baseline_metrics"], indent=2, default=float))
    (out/"data_quality.json").write_text(json.dumps(result["quality"], indent=2, default=float))
    (out/"grade_de_dti_over_25_demo.json").write_text(json.dumps(result["grade_de_target"], indent=2))
    for key in ["grade_segments","income_segments","term_segments","dti_segments","purpose_segments"]:
        result[key].to_csv(out/f"{key}.csv", index=False)
    result["predictions"].to_csv(out/"test_predictions.csv", index=False)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default="data/sample/synthetic_loans.csv")
    p.add_argument("--output", default="outputs")
    a=p.parse_args(); df=pd.read_csv(a.input); result=run_analysis(df); write_outputs(result,a.output)
    print(json.dumps({k:v for k,v in result["metrics"].items() if k not in ["classification_report","confusion_matrix"]}, indent=2))
    print(f"Analysis outputs written to {Path(a.output).resolve()}")
if __name__ == "__main__": main()
