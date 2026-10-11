from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import pytest
from src.generate_demo_data import generate_demo_data
from src.validate_data import validate_dataframe
from src.analyze import run_analysis, FEATURES, segment_table
from src.prepare_lendingclub import normalize_chunk, prepare_lendingclub

ROOT = Path(__file__).resolve().parents[1]

def sample():
    return pd.read_csv(ROOT / "data/sample/synthetic_loans.csv")

def test_demo_dataset_is_deterministic_and_explicitly_labeled():
    a = generate_demo_data(500, seed=4)
    b = generate_demo_data(500, seed=4)
    pd.testing.assert_frame_equal(a, b)
    assert len(a) == 500
    assert a.loan_id.str.startswith("SYN").all()
    assert set(a.default_flag.unique()) == {0, 1}

def test_demo_dataset_schema_and_quality():
    df = sample(); result = validate_dataframe(df)
    assert len(df) == 8000
    assert result["passed"] is True
    assert result["duplicate_loan_ids"] == 0
    assert result["invalid_target_rows"] == 0
    assert set(df.default_flag.unique()) == {0, 1}

def test_pipeline_produces_valid_holdout_metrics_and_segments():
    result = run_analysis(sample()); m = result["metrics"]
    assert 0 <= m["roc_auc"] <= 1
    assert 0 <= m["average_precision"] <= 1
    assert 0 <= m["precision_default"] <= 1
    assert 0 <= m["recall_default"] <= 1
    assert m["train_rows"] + m["validation_rows"] + m["test_rows"] == m["rows"]
    assert sum(sum(row) for row in m["confusion_matrix"]) == m["test_rows"]
    assert m["split_method"] == "out_of_time_70_15_15"
    assert 0.05 <= m["threshold"] <= 0.50
    assert set(result["grade_segments"].grade.astype(str)) <= set("ABCDEFG")
    assert {"ci_95_low_pct", "ci_95_high_pct"}.issubset(result["grade_segments"].columns)

def test_features_exclude_identifiers_dates_outcomes_and_status():
    prohibited = {"loan_id", "issue_date", "default_flag", "loan_status", "recoveries", "total_pymnt"}
    assert not prohibited.intersection(FEATURES)

def test_validation_rejects_duplicate_ids():
    df = sample(); df.loc[1, "loan_id"] = df.loc[0, "loan_id"]
    assert validate_dataframe(df)["passed"] is False

def test_validation_rejects_missing_required_column():
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dataframe(sample().drop(columns=["dti"]))

def test_lendingclub_normalizer_excludes_unresolved_statuses_and_maps_target():
    raw = pd.DataFrame({
        "id": ["101", "102", "103", "104"],
        "issue_d": ["Jan-2018", "Feb-2018", "Mar-2018", "Apr-2018"],
        "loan_amnt": [10000, 15000, 8000, 5000], "annual_inc": [60000, 70000, 45000, 52000],
        "dti": [15, 22, 12, 25], "int_rate": ["10.5%", "16.2%", "11.0%", "9.5%"],
        "term": ["36 months", "60 months", "36 months", "36 months"],
        "grade": ["B", "D", "C", "A"], "emp_length": ["5 years"]*4,
        "home_ownership": ["RENT"]*4, "purpose": ["debt_consolidation"]*4,
        "delinq_2yrs": [0, 1, 0, 0], "loan_status": ["Fully Paid", "Charged Off", "Current", "Late (31-120 days)"]
    })
    out = normalize_chunk(raw)
    assert list(out.loan_id) == ["101", "102"]
    assert out.default_flag.tolist() == [0, 1]
    assert out.term_months.tolist() == [36, 60]
    assert out.issue_date.tolist() == ["2018-01-01", "2018-02-01"]

def test_segment_confidence_intervals_enclose_observed_rate():
    df = sample()
    tab = segment_table(df, "grade")
    assert (tab.ci_95_low_pct <= tab.default_rate_pct).all()
    assert (tab.ci_95_high_pct >= tab.default_rate_pct).all()


def test_chunked_import_writes_only_resolved_rows(tmp_path):
    raw = pd.DataFrame({
        "id": ["201", "202", "203"], "issue_d": ["Jan-2018", "Feb-2018", "Mar-2018"],
        "loan_amnt": [10000, 15000, 9000], "annual_inc": [60000, 70000, 45000],
        "dti": [15, 22, 12], "int_rate": ["10.5%", "16.2%", "11.0%"],
        "term": ["36 months", "60 months", "36 months"], "grade": ["B", "D", "C"],
        "emp_length": ["5 years"]*3, "home_ownership": ["RENT"]*3,
        "purpose": ["debt_consolidation"]*3, "delinq_2yrs": [0, 1, 0],
        "loan_status": ["Fully Paid", "Charged Off", "Current"]
    })
    raw_file = tmp_path / "raw.csv"; out_file = tmp_path / "normalized.csv"
    raw.to_csv(raw_file, index=False)
    result = prepare_lendingclub(str(raw_file), str(out_file), sample_size=10, chunksize=2, seed=12)
    assert out_file.exists()
    assert len(result) == 2
    assert set(result.loan_status) == {"Fully Paid", "Charged Off"}
    assert result.default_flag.sum() == 1
