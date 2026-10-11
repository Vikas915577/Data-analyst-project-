from __future__ import annotations
import argparse
import pandas as pd

REQUIRED = ["loan_id", "issue_date", "loan_amnt", "annual_inc", "dti", "int_rate", "term_months", "grade", "emp_length", "home_ownership", "purpose", "delinq_2yrs", "default_flag"]

def validate_dataframe(df: pd.DataFrame) -> dict:
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    if df.empty:
        raise ValueError("Dataset has zero rows")
    if df["loan_id"].isna().any():
        raise ValueError("loan_id contains null values")
    duplicates = int(df["loan_id"].duplicated().sum())
    invalid_target = int((~df["default_flag"].isin([0, 1])).sum())
    invalid_amount = int((pd.to_numeric(df["loan_amnt"], errors="coerce") <= 0).sum())
    invalid_dti = int(((pd.to_numeric(df["dti"], errors="coerce") < 0) | (pd.to_numeric(df["dti"], errors="coerce") > 100)).sum())
    missing_pct = (df[REQUIRED].isna().mean().mul(100).round(2)).to_dict()
    return {"rows": int(len(df)), "columns": int(len(df.columns)), "duplicate_loan_ids": duplicates, "invalid_target_rows": invalid_target, "invalid_loan_amount_rows": invalid_amount, "suspicious_dti_rows": invalid_dti, "default_rate_pct": round(float(pd.to_numeric(df["default_flag"], errors="coerce").mean() * 100), 2), "missing_pct": missing_pct, "passed": duplicates == 0 and invalid_target == 0 and invalid_amount == 0 and invalid_dti == 0}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="data/sample/synthetic_loans.csv")
    args = parser.parse_args()
    df = pd.read_csv(args.input)
    report = validate_dataframe(df)
    print(pd.Series({k:v for k,v in report.items() if k != "missing_pct"}).to_string())
    print("\nMissingness (%):")
    print(pd.Series(report["missing_pct"]).to_string())
    if not report["passed"]:
        raise SystemExit("Validation failed; review issues above.")
    print("\nValidation passed.")
if __name__ == "__main__": main()
