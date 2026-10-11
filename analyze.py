from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report, balanced_accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from src.validate_data import validate_dataframe

NUMERIC = ["loan_amnt", "annual_inc", "dti", "int_rate", "term_months", "delinq_2yrs"]
CATEGORICAL = ["grade", "emp_length", "home_ownership", "purpose"]
FEATURES = NUMERIC + CATEGORICAL  # intentionally excludes issue_date, loan_id, and target

def run_analysis(df: pd.DataFrame) -> dict:
    quality = validate_dataframe(df)
    if not quality["passed"]: raise ValueError("Data quality checks failed")
    data = df.copy()
    data["issue_date"] = pd.to_datetime(data["issue_date"], errors="coerce")
    target = data["default_flag"].astype(int)
    if target.nunique() < 2: raise ValueError("Target must contain both 0 and 1")
    segment = data.groupby("grade", dropna=False).agg(loans=("loan_id", "count"), defaults=("default_flag", "sum"), default_rate=("default_flag", "mean")).reset_index()
    segment["default_rate_pct"] = (segment["default_rate"] * 100).round(2)
    dti_band = pd.cut(data["dti"], bins=[-0.001, 10, 20, 30, 100.001], labels=["<10", "10–<20", "20–<30", "30+"])
    dti = data.assign(dti_band=dti_band).groupby("dti_band", observed=False).agg(loans=("loan_id", "count"), defaults=("default_flag", "sum"), default_rate=("default_flag", "mean")).reset_index()
    dti["default_rate_pct"] = (dti["default_rate"] * 100).round(2)
    X = data[FEATURES].copy()
    y = target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    preprocessor = ColumnTransformer([("num", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), NUMERIC), ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("encoder", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL)])
    model = Pipeline([("preprocess", preprocessor), ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))])
    model.fit(X_train, y_train)
    prob = model.predict_proba(X_test)[:, 1]
    pred = (prob >= 0.5).astype(int)
    metrics = {"rows": len(data), "defaults": int(y.sum()), "default_rate_pct": round(float(y.mean()*100), 2), "train_rows": len(X_train), "test_rows": len(X_test), "roc_auc": round(float(roc_auc_score(y_test, prob)), 4), "balanced_accuracy": round(float(balanced_accuracy_score(y_test, pred)), 4), "precision_default": round(float(precision_score(y_test, pred, zero_division=0)), 4), "recall_default": round(float(recall_score(y_test, pred, zero_division=0)), 4), "f1_default": round(float(f1_score(y_test, pred, zero_division=0)), 4), "threshold": 0.5, "confusion_matrix": confusion_matrix(y_test, pred, labels=[0,1]).tolist(), "classification_report": classification_report(y_test, pred, labels=[0,1], target_names=["non_default", "default"], output_dict=True, zero_division=0)}
    return {"metrics": metrics, "grade_segments": segment, "dti_segments": dti, "quality": quality}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--input", default="data/sample/synthetic_loans.csv"); p.add_argument("--output", default="outputs"); args=p.parse_args()
    df=pd.read_csv(args.input); result=run_analysis(df); out=Path(args.output); out.mkdir(parents=True, exist_ok=True)
    (out/"metrics.json").write_text(json.dumps(result["metrics"], indent=2))
    result["grade_segments"].to_csv(out/"default_rate_by_grade.csv", index=False)
    result["dti_segments"].to_csv(out/"default_rate_by_dti.csv", index=False)
    (out/"data_quality.json").write_text(json.dumps(result["quality"], indent=2))
    print(json.dumps(result["metrics"], indent=2)); print(f"\nOutputs written to {out.resolve()}")
if __name__ == "__main__": main()
