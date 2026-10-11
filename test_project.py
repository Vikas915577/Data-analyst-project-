from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import pandas as pd
import pytest
from src.validate_data import validate_dataframe
from src.analyze import run_analysis, FEATURES

def sample(): return pd.read_csv(ROOT / "data/sample/synthetic_loans.csv")

def test_demo_dataset_schema_and_quality():
    df=sample(); result=validate_dataframe(df)
    assert len(df)==5000
    assert result["passed"] is True
    assert result["duplicate_loan_ids"] == 0
    assert set(df.default_flag.unique()) == {0,1}

def test_pipeline_metrics_and_segments():
    result=run_analysis(sample()); m=result["metrics"]
    assert 0 <= m["roc_auc"] <= 1
    assert 0 <= m["precision_default"] <= 1
    assert 0 <= m["recall_default"] <= 1
    assert sum(sum(row) for row in m["confusion_matrix"]) == m["test_rows"]
    assert set(result["grade_segments"].grade) <= set("ABCDEFG")

def test_features_exclude_identifiers_and_target():
    assert "loan_id" not in FEATURES
    assert "issue_date" not in FEATURES
    assert "default_flag" not in FEATURES

def test_validation_rejects_duplicate_ids():
    df=sample(); df.loc[1,"loan_id"]=df.loc[0,"loan_id"]
    assert validate_dataframe(df)["passed"] is False

def test_validation_rejects_missing_required_column():
    df=sample().drop(columns=["dti"])
    with pytest.raises(ValueError, match="Missing required columns"):
        validate_dataframe(df)
