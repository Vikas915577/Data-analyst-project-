"""Schema and data-quality checks for normalized loan-level data."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import pandas as pd

REQUIRED = ["loan_id", "issue_date", "loan_amnt", "annual_inc", "dti", "int_rate", "term_months", "grade", "emp_length", "home_ownership", "purpose", "delinq_2yrs", "default_flag"]
NUMERIC_BOUNDS = {
    "loan_amnt": (0, None), "annual_inc": (0, None), "dti": (0, 100),
    "int_rate": (0, 100), "term_months": (1, 120), "delinq_2yrs": (0, None),
}

def validate_dataframe(df: pd.DataFrame) -> dict:
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    if df.empty:
        raise ValueError("Dataset has zero rows")
    work = df.copy()
    work["issue_date"] = pd.to_datetime(work["issue_date"], errors="coerce")
    for col in NUMERIC_BOUNDS:
        work[col] = pd.to_numeric(work[col], errors="coerce")
    target = pd.to_numeric(work["default_flag"], errors="coerce")
    dup_count = int(work["loan_id"].duplicated().sum())
    null_ids = int(work["loan_id"].isna().sum())
    invalid_target = int((target.isna() | ~target.isin([0, 1])).sum())
    invalid_ranges = {}
    for col, (low, high) in NUMERIC_BOUNDS.items():
        bad = work[col].notna() & (work[col] <= low if col in ["loan_amnt"] else work[col] < low)
        if high is not None:
            bad = bad | (work[col].notna() & (work[col] > high))
        invalid_ranges[col] = int(bad.sum())
    missing_pct = work[REQUIRED].isna().mean().mul(100).round(2).to_dict()
    valid_target = target[target.isin([0, 1])]
    issue_date_invalid = int(work["issue_date"].isna().sum())
    target_classes = sorted(valid_target.dropna().astype(int).unique().tolist())
    problems = []
    if dup_count: problems.append("duplicate loan_id values")
    if null_ids: problems.append("missing loan_id values")
    if invalid_target: problems.append("invalid or missing binary target")
    if any(invalid_ranges.values()): problems.append("numeric values outside permitted ranges")
    if issue_date_invalid: problems.append("invalid or missing issue_date values")
    if len(target_classes) != 2: problems.append("target must contain both 0 and 1 classes")
    passed = len(problems) == 0
    return {
        "rows": int(len(work)), "columns": int(len(work.columns)),
        "duplicate_loan_ids": dup_count, "missing_loan_ids": null_ids,
        "invalid_target_rows": invalid_target, "invalid_ranges_by_column": invalid_ranges,
        "invalid_issue_dates": issue_date_invalid, "target_classes": target_classes,
        "default_rate_pct": round(float(valid_target.mean() * 100), 2) if len(valid_target) else None,
        "missing_pct": missing_pct, "problems": problems, "passed": passed,
    }

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", default="data/sample/synthetic_loans.csv")
    p.add_argument("--output", default="outputs/data_quality.json")
    args=p.parse_args()
    df=pd.read_csv(args.input)
    result=validate_dataframe(df)
    print(json.dumps(result, indent=2))
    path=Path(args.output); path.parent.mkdir(parents=True, exist_ok=True); path.write_text(json.dumps(result, indent=2))
    if not result["passed"]: raise SystemExit("Validation failed; review data-quality report.")
    print("Validation passed.")
if __name__ == "__main__": main()
