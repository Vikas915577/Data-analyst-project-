# Credit Risk & Loan Analytics

A reproducible portfolio project exploring loan default patterns with SQL, Python, and an interactive Streamlit dashboard. The goal is to demonstrate end-to-end analytics: data validation, exploratory analysis, segment risk rates, baseline classification, model evaluation, and decision-aware caveats.

> **Data integrity:** the bundled dataset is synthetic demo data, not actual LendingClub records. Do not claim empirical LendingClub findings or reuse numeric outputs as real-world facts. The schema is LendingClub-inspired. See [`data/sample/DATA_NOTICE.md`](data/sample/DATA_NOTICE.md).

## Business question
Which loan-originations segments show higher simulated default rates, and how can an analyst evaluate a simple baseline model without data leakage? This is exploratory education—not a credit decisioning system.

## Features
- Responsive Streamlit dashboard with filters and KPIs
- Data-quality checks for missing values, duplicates, invalid ranges and target coverage
- Default-rate segmentation by grade, term, purpose, and DTI band
- Baseline Logistic Regression pipeline with preprocessing fitted on training data only
- ROC-AUC, precision, recall, F1, confusion matrix, and threshold caveats
- PostgreSQL-compatible SQL schema and analysis queries
- Unit tests for schema, metrics, and leakage-safe feature selection

## Run locally
Python 3.10+ recommended. From this directory:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.validate_data --input data/sample/synthetic_loans.csv
python -m src.analyze --input data/sample/synthetic_loans.csv --output outputs
streamlit run app/streamlit_app.py
pytest -q
```

The dashboard opens locally in your browser. In Streamlit Community Cloud, set the main file path to `app/streamlit_app.py`.

## Bring your own permitted dataset
1. Place your permitted CSV at `data/raw/loans.csv` (raw data is git-ignored).
2. Map source columns to this project's documented schema: `loan_id`, `issue_date`, `loan_amnt`, `annual_inc`, `dti`, `int_rate`, `term_months`, `grade`, `emp_length`, `home_ownership`, `purpose`, `delinq_2yrs`, `default_flag`.
3. `default_flag` must be a clearly defined binary outcome (1=default/charged-off according to the source's documented mapping; 0=non-default eligible comparison). Exclude unresolved/current statuses from binary modeling rather than silently treating them as non-default.
4. Check the source data dictionary, time period, status mapping, missingness, and legal terms before analysis.
5. Run validation and analysis commands against your file. Do not publish personally identifying information or raw records.

## Methodology
- Unit of analysis: one loan record.
- Target: `default_flag`; its exact definition must be documented for any real dataset.
- Predictors: only fields intended to be known at or before origination. Payment history, recovery amounts, last payment dates, and final loan status must not be used as predictors.
- Split: stratified random train/test split for a baseline demonstration. For real historical data, prefer an out-of-time split and assess drift.
- Evaluation: use more than accuracy. Defaults are often a minority class, so precision/recall, F1, ROC-AUC, and the confusion matrix provide complementary views. Thresholds should reflect business costs and be calibrated/validated before use.
- No causal claims: segment differences are associations, not proof that a feature causes default.

## Repository structure
```text
app/streamlit_app.py       interactive dashboard
src/validate_data.py       schema and quality checks
src/analyze.py             EDA and baseline model pipeline
sql/schema.sql             PostgreSQL table definition
sql/analysis_queries.sql   reproducible segment queries
data/sample/               synthetic demo data + notice
tests/                     automated tests
docs/                      methodology and data dictionary
```

## Research and references
- LendingClub-style field definitions and status context: [LendingClub data cleaning notes/data dictionary example](https://github.com/elsalmi/LendingClub/blob/master/Data-Cleaning.md). This is a third-party explanatory reference, not the dataset bundled here.
- Research using historical LendingClub loans describes the importance of distinguishing accepted-loan status and the limits of available fields: [Peer-to-peer loan acceptance and default prediction (2020)](https://pmc.ncbi.nlm.nih.gov/articles/PMC7353984/).
- Evaluation metrics for imbalanced classification: [scikit-learn model evaluation documentation](https://scikit-learn.org/stable/modules/model_evaluation.html) and [precision-recall example](https://scikit-learn.org/stable/auto_examples/model_selection/plot_precision_recall.html).

## Limitations and responsible use
This demo is synthetic, not representative of real borrowers, any lender's portfolio, or current credit conditions. It is not validated for underwriting, pricing, collections, or individual decisions. Real credit modeling requires source review, temporal validation, calibration, fairness and legal review, monitoring, explainability, and appropriate governance. Do not use protected or sensitive attributes as casual model features.

## License
Code: MIT (see `LICENSE`). The synthetic demo data is generated for this project. External datasets remain subject to their own terms.
