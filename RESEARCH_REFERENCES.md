# Research and source references

These references guide project methodology; they do not verify findings from the bundled synthetic sample.

1. **Historical LendingClub field/status workflow (third-party teaching example):** https://github.com/elsalmi/LendingClub/blob/master/Data-Cleaning.md — demonstrates filtering historical loans to resolved outcomes such as `Fully Paid` and `Charged Off`; verify exact field meanings against the data dictionary for the copy you obtain.
2. **Model evaluation metrics:** https://scikit-learn.org/stable/modules/model_evaluation.html — official documentation for ROC-AUC, precision, recall, F1, average precision and related metrics.
3. **Threshold selection:** https://scikit-learn.org/stable/modules/classification_threshold.html — distinguishes probability/ranking from the decision threshold chosen for an action.
4. **Probability calibration:** https://scikit-learn.org/stable/modules/calibration.html — explains how calibration affects interpretation of predicted probabilities.
5. **Credit adverse-action explanations:** https://www.consumerfinance.gov/compliance/circulars/circular-2022-03-adverse-action-notification-requirements-in-connection-with-credit-decisions-based-on-complex-algorithms/ — U.S.-specific guidance explaining that complex models do not remove requirements for specific reasons for adverse action. This is a reference for responsible modeling, not India-specific legal advice.
6. **Alternative open credit dataset (not used in this project):** https://archive.ics.uci.edu/dataset/350/default%2Bof%2Bcredit%2Bcard%2Bclients — UCI dataset of 30,000 credit-card records, licensed CC BY 4.0; it is a different dataset from LendingClub.

Accessed 11 October 2026. Source notes and licensing terms should be rechecked before external publication.
