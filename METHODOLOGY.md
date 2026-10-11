# Methodology and analytical guardrails

## Business question
Which loan origination segments show higher observed default rates, and how does a simple baseline classifier rank risk on a later time period?

## Outcome definition
For the optional LendingClub preparation pipeline, the binary target is explicitly defined as `Charged Off = 1` and `Fully Paid = 0`. Other statuses (including `Current`, `Late`, `In Grace Period`, and unresolved outcomes) are excluded from this binary analysis rather than silently counted as non-defaults. This is a historical, resolved-outcome sample; it is not the same thing as all applications or all currently active loans.

## Unit, features and leakage
One row represents one loan. Candidate predictors are intended to be available at origination: loan amount, annual income, DTI, interest rate, term, grade, employment length, housing status, loan purpose and prior two-year delinquencies. The ID, issue date, final status, target, payments, recoveries, collections and other post-origination fields are not model features. The issue date is used only to order train/validation/test periods.

## Segmentation
Default rate is `defaults / eligible resolved loans`. Every displayed rate should be read alongside its denominator. CSV segment outputs include 95% Wilson intervals to help avoid over-interpreting small segments. Income bands and DTI bands are fixed and documented so that the group definition remains comparable across runs.

## Evaluation
The default split is chronological: earliest 70% of issue-date distribution for training, next 15% for validation and latest 15% for final testing. A stratified random fallback is explicitly flagged only when a time-based split cannot contain both classes with enough records. Numeric imputation/scaling and categorical imputation/encoding are fitted inside a pipeline on the training data only. The validation period selects an illustrative F1 threshold from 0.05–0.50; the final test period is not used to select it.

Reported metrics include ROC-AUC, average precision (PR-AUC/AP), balanced accuracy, precision, recall, F1, Brier score and confusion matrix. A prior-only dummy model is included as a baseline. The validation-selected threshold is educational—not an underwriting policy. Credit models require costs and decision rules defined before threshold selection, plus calibration, stability, temporal validation, explainability, fair-lending/legal review and governance.

## Scope limitations
The bundled data is generated for software QA and demonstration only. Its default rate and segments are not empirical LendingClub findings and cannot substantiate a real-world claim such as a 28.4% default rate. Repeat the analysis on a documented, permitted source dataset before reporting any empirical conclusions.
