# Analysis walkthrough

## Questions answered
1. What is the eligible loan volume and observed default rate?
2. How do rates differ by grade, income band, DTI band, term and purpose?
3. What is the volume and default rate for grades D/E when DTI exceeds 25%?
4. Does a simple model outperform a prior-only baseline on a later period?
5. Are missingness, duplicates, target labels and numeric ranges safe enough for exploratory analysis?

## Run the analysis

```bash
python -m src.validate_data --input data/sample/synthetic_loans.csv --output outputs/data_quality.json
python -m src.analyze --input data/sample/synthetic_loans.csv --output outputs
```

The `outputs/` folder contains segment tables, metrics, target-segment calculation and test-set predictions. Outputs are reproducible for a fixed input and library versions. The default bundled run is explicitly a synthetic demonstration.

## How to discuss this project in an interview

- Explain how unresolved loan statuses are excluded to reduce outcome-label ambiguity.
- Explain why post-origination payment and recovery columns would be leakage if used to predict an origination-time outcome.
- Describe the difference between a segment default rate and an individual model score.
- Explain why segment denominators and confidence intervals matter.
- Compare logistic regression to the prior-only baseline and interpret PR-AUC alongside ROC-AUC.
- Explain why the validation set—not the final test set—selects the illustrative threshold.
- State that synthetic data validates code paths, not real-world business findings.
