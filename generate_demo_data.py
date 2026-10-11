"""Generate deterministic synthetic loan data for a safe, instantly runnable demo.

This dataset is not sourced from LendingClub and must never be described as real borrower data.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 20261011

def generate_demo_data(n: int = 8_000, seed: int = SEED) -> pd.DataFrame:
    if n < 100:
        raise ValueError("n must be at least 100 to support meaningful train/test splits")
    rng = np.random.default_rng(seed)
    grades = np.array(list("ABCDEFG"))
    grade_probs = np.array([0.16, 0.23, 0.22, 0.17, 0.11, 0.07, 0.04])
    grade = rng.choice(grades, size=n, p=grade_probs)
    grade_idx = pd.Series(grade).map({g:i for i,g in enumerate(grades)}).to_numpy()
    issue_month = rng.integers(0, 72, size=n)
    issue_date = pd.to_datetime("2013-01-01") + pd.to_timedelta(issue_month * 30, unit="D")
    loan_amnt = np.round(np.clip(rng.lognormal(mean=9.45, sigma=0.48, size=n), 1_000, 40_000), 0).astype(int)
    annual_inc = np.round(np.clip(rng.lognormal(mean=10.85, sigma=0.62, size=n), 12_000, 250_000), 0).astype(int)
    dti = np.round(np.clip(rng.normal(17 + grade_idx * 1.6, 8.5, size=n), 0, 60), 2)
    base_rate = np.array([6.5, 8.5, 11.0, 14.5, 18.0, 22.0, 26.0])[grade_idx]
    int_rate = np.round(np.clip(base_rate + rng.normal(0, 1.7, n), 5, 32), 2)
    term_months = rng.choice([36, 60], size=n, p=[0.72, 0.28])
    emp_length = rng.choice(["<1 year", "1-3 years", "4-6 years", "7-9 years", "10+ years"], size=n, p=[.10,.22,.23,.18,.27])
    home = rng.choice(["MORTGAGE", "RENT", "OWN", "OTHER"], size=n, p=[.43,.40,.15,.02])
    purpose = rng.choice(["debt_consolidation", "credit_card", "home_improvement", "major_purchase", "medical", "other"], size=n, p=[.48,.20,.12,.08,.04,.08])
    delinq = np.clip(rng.poisson(0.25 + grade_idx * 0.11, size=n), 0, 5)
    # Risk score is intentionally synthetic; it creates plausible patterns, not evidence about real borrowers.
    logit = -3.55 + grade_idx * 0.43 + np.maximum(dti - 20, 0) * 0.027 + (term_months == 60) * 0.35 + delinq * 0.22 + (annual_inc < 35_000) * 0.18
    p_default = 1 / (1 + np.exp(-logit))
    default_flag = rng.binomial(1, p_default)
    loan_id = [f"SYN{i:07d}" for i in range(1, n + 1)]
    df = pd.DataFrame({
        "loan_id": loan_id, "issue_date": issue_date.strftime("%Y-%m-%d"), "loan_amnt": loan_amnt,
        "annual_inc": annual_inc, "dti": dti, "int_rate": int_rate, "term_months": term_months,
        "grade": grade, "emp_length": emp_length, "home_ownership": home, "purpose": purpose,
        "delinq_2yrs": delinq, "default_flag": default_flag,
        "loan_status": np.where(default_flag == 1, "Charged Off", "Fully Paid"),
    })
    return df

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rows", type=int, default=8_000)
    p.add_argument("--output", default="data/sample/synthetic_loans.csv")
    p.add_argument("--seed", type=int, default=SEED)
    a=p.parse_args(); out=Path(a.output); out.parent.mkdir(parents=True, exist_ok=True)
    df=generate_demo_data(a.rows, a.seed); df.to_csv(out, index=False)
    print(f"Wrote {len(df):,} synthetic demo rows to {out}")
    print(f"Synthetic default rate: {df.default_flag.mean():.1%} (demo only)")
if __name__ == "__main__": main()
