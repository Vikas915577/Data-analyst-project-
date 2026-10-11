# Analysis walkthrough

## Questions
1. What share of eligible demo loans are labeled default?
2. How do rates vary across grade, term, purpose and DTI band?
3. Does a leakage-aware baseline discriminate simulated outcomes on a holdout?

## Reproduce
Run `python -m src.analyze --input data/sample/synthetic_loans.csv --output outputs`. The script writes metrics JSON and segment CSVs.

## Read the metrics responsibly
- `default_rate_pct`: simulated defaults divided by all simulated loans in the group.
- `ROC-AUC`: ranking discrimination on the held-out set; it is not calibration and does not define an operating threshold.
- `precision_default`: of loans predicted default at threshold 0.5, share that are actually labeled default.
- `recall_default`: of loans labeled default, share detected at threshold 0.5.
- `F1`: harmonic mean of precision and recall.

These are demo outputs only. Do not paste their values into a resume as real business findings. For real historical data, use an out-of-time evaluation and assess calibration, stability, and subgroup performance.
