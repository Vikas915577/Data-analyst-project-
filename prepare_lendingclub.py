"""Normalize public LendingClub accepted-loan exports into analysis-ready rows.

Input is not bundled: users must obtain a permitted historical export themselves.
Only final outcomes Fully Paid and Charged Off are retained. A reproducible,
uniform reservoir sample is used when --sample-size is set.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

SOURCE_COLUMNS = ["id", "issue_d", "loan_amnt", "annual_inc", "dti", "int_rate", "term", "grade", "emp_length", "home_ownership", "purpose", "delinq_2yrs", "loan_status"]
OUTPUT_COLUMNS = ["loan_id", "issue_date", "loan_amnt", "annual_inc", "dti", "int_rate", "term_months", "grade", "emp_length", "home_ownership", "purpose", "delinq_2yrs", "default_flag", "loan_status"]

def normalize_chunk(raw: pd.DataFrame) -> pd.DataFrame:
    missing = [c for c in SOURCE_COLUMNS if c not in raw.columns]
    if missing: raise ValueError(f"Raw CSV is missing required LendingClub columns: {missing}")
    x = raw.loc[raw["loan_status"].isin(["Fully Paid", "Charged Off"])].copy()
    if x.empty: return pd.DataFrame(columns=OUTPUT_COLUMNS)
    x["loan_id"] = x["id"].astype("string").str.strip()
    # Raw LendingClub issue_d is commonly 'Dec-2018'; ISO dates are also accepted.
    issue_text = x["issue_d"].astype("string")
    d = pd.to_datetime(issue_text, format="%b-%Y", errors="coerce")
    failed = d.isna()
    if failed.any():
        # Apply date inference only to non-standard rows, avoiding noise on normal %b-%Y values.
        d.loc[failed] = pd.to_datetime(issue_text.loc[failed], format="mixed", errors="coerce")
    x["issue_date"] = d.dt.strftime("%Y-%m-%d")
    for c in ["loan_amnt", "annual_inc", "dti", "delinq_2yrs"]:
        x[c] = pd.to_numeric(x[c], errors="coerce")
    x["int_rate"] = pd.to_numeric(x["int_rate"].astype(str).str.replace("%", "", regex=False), errors="coerce")
    x["term_months"] = pd.to_numeric(x["term"].astype(str).str.extract(r"(\d+)")[0], errors="coerce")
    x["default_flag"] = (x["loan_status"] == "Charged Off").astype("int8")
    x = x.rename(columns={"grade": "grade"})
    x = x[OUTPUT_COLUMNS]
    x = x.dropna(subset=["loan_id", "issue_date", "loan_amnt", "default_flag"])
    x = x.drop_duplicates(subset=["loan_id"], keep="first")
    return x

def prepare_lendingclub(input_path: str, output_path: str, sample_size: int = 50_000, chunksize: int = 150_000, seed: int = 42) -> pd.DataFrame:
    if sample_size <= 0: raise ValueError("sample_size must be positive")
    rng = np.random.default_rng(seed)
    reservoir = pd.DataFrame(columns=OUTPUT_COLUMNS + ["__key"])
    total_eligible = 0
    for chunk in pd.read_csv(input_path, usecols=lambda c: c in SOURCE_COLUMNS, chunksize=chunksize, low_memory=False):
        normalized = normalize_chunk(chunk)
        if normalized.empty: continue
        total_eligible += len(normalized)
        normalized["__key"] = rng.random(len(normalized))
        if reservoir.empty:
            reservoir = normalized.reset_index(drop=True)
        else:
            reservoir = pd.concat([reservoir, normalized], ignore_index=True)
        if len(reservoir) > sample_size:
            reservoir = reservoir.nsmallest(sample_size, "__key").reset_index(drop=True)
        print(f"Eligible resolved rows scanned: {total_eligible:,}; sample retained: {len(reservoir):,}")
    if reservoir.empty:
        raise ValueError("No eligible Fully Paid / Charged Off rows found. Check source statuses and column names.")
    result = reservoir.drop(columns="__key").sort_values(["issue_date", "loan_id"]).reset_index(drop=True)
    out = Path(output_path); out.parent.mkdir(parents=True, exist_ok=True); result.to_csv(out, index=False)
    print(f"Wrote {len(result):,} normalized rows to {out}; eligible scanned={total_eligible:,}.")
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", required=True, help="Path to accepted_2007_to_2018Q4.csv")
    p.add_argument("--output", default="data/processed/lendingclub_sample.csv")
    p.add_argument("--sample-size", type=int, default=50_000)
    p.add_argument("--chunksize", type=int, default=150_000)
    p.add_argument("--seed", type=int, default=42)
    a=p.parse_args(); prepare_lendingclub(a.input, a.output, a.sample_size, a.chunksize, a.seed)
if __name__ == "__main__": main()
