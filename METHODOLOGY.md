# Methodology and decision framework

1. **Define the outcome.** In the demo, `default_flag=1` is a synthetic positive class. With real data, document exactly which statuses map to default and which resolved statuses are eligible controls. Current/open loans are censored outcomes, not automatically non-defaults.
2. **Validate before modeling.** Check row counts, unique loan identifiers, missing values, ranges, category coverage, and target prevalence.
3. **Explore rates with denominators.** Default rate = defaulted eligible loans / all eligible loans in that segment. Show both rate and segment count; small segments are less stable.
4. **Avoid target leakage.** Only use origination-time features. Do not include post-origination payment, recovery, final status, or collections variables.
5. **Split and preprocess safely.** Use a stratified holdout. Fit imputers, encoders, and model only on training rows via a Pipeline/ColumnTransformer.
6. **Evaluate trade-offs.** Report ROC-AUC plus precision, recall, F1, and confusion matrix at an explicitly chosen threshold. A threshold is not a business decision until error costs and capacity are considered.
7. **Interpret carefully.** Correlation does not imply causation; synthetic patterns do not generalize to real portfolios. For real data use time-based validation, calibration, subgroup performance/fairness checks, and monitoring.
