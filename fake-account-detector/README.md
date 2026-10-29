# Fake Social Media Account Detection

Scikit-learn project that compares a dummy classifier, logistic regression, and random forest on account profile statistics. The fitted feature builder and preprocessing steps are saved with the classifier so prediction uses the same transformations as training.

## Data and audit

The supplied workbooks are copied into `data/raw/` so the project runs from its own directory. Those source copies and fitted model artifacts are excluded from Git. The copies are unchanged; processed files and reports live separately. The audit is in `reports/data_audit.md` (machine-readable companion: `reports/data_audit.json`).

Audit findings that affect interpretation:

- `dataset` maps directly to class when present, so it is excluded from features. `RAND`, identifiers, account names/handles, URLs, image URLs, location, free-text description, both timestamps, and the target are excluded. The `updated` snapshot timestamp has one observed value per training source, so timestamp-derived account age is omitted to avoid source leakage.
- Training and test contain exact shared records and substantial overlap in account handles and profile image URLs. Final test metrics are descriptive and are not evidence of independent generalization.
- Some count columns contain fractional values and IDs often contain repeated zeros. Values are preserved and coerced to numeric for the model; source rows are not silently altered.
- Free-text descriptions and free-form locations are omitted from this baseline because they are sparse or high-cardinality profile text; text modeling can be evaluated as a separate experiment.
- The provided test file is named `merged testing.xlsx`; the requested `merged testing(1).xlsx` was not present. The available file is used and this discrepancy is recorded in the audit.

## Setup

Python 3.12+ is recommended (the dependency versions in `requirements.txt` are pinned to the verified environment).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Commands

Run the read-only data audit:

```bash
python -m src.data.audit_data
```

Train and select using a reproducible stratified holdout from the combined training workbooks. This command does not load the test workbook:

```bash
python train.py
```

Evaluate the selected model once on the labeled test workbook after training:

```bash
python evaluate.py
```

Training writes validation comparisons and model selection to `reports/model_selection.json`. Evaluation writes final metrics to `reports/model_results.json` and a confusion matrix to `reports/evaluation_metrics.png`. The test set has record/account overlap with training; read its warning before interpreting results.

Predict a new CSV or Excel file (all five core count features are required; other model inputs are optional and imputed):

```bash
python predict.py new_accounts.xlsx --output predictions.xlsx
python predict.py new_accounts.csv --output predictions.xlsx
```

The output preserves input columns and appends `predicted_is_fake` and `fake_probability`. A score is not a guarantee of authenticity. The input file is never modified.

## Project layout

```text
data/raw/             supplied workbook copies (gitignored)
data/processed/       optional prepared data (gitignored)
src/data/             loading, audit, validation, cleaning
src/features/         reusable engineered features and preprocessing
src/models/           training, selection, and prediction
src/evaluation/       metrics and overlap diagnostics
models/               serialized complete pipeline (gitignored)
reports/              audit and evaluation output
tests/                validation, preprocessing, training, prediction tests
```

## Evaluation design and limits

The 20% stratified validation holdout is drawn only from the combined training sources and is used for model selection. All preprocessing is inside the estimator pipeline and is learned on its fit partition. The final selected pipeline is refit on all training records before test evaluation. `is_fake` is checked as ground truth at evaluation and removed before prediction. Test labels never affect feature construction, imputation, encoding, or model selection.

This is a legacy, highly transformed dataset, with zero IDs, fractional count values, a source marker associated with class, and substantial training/test overlap. The source marker is excluded, but overlapping identities remain a major limitation of the final test estimate. Collecting a fresh, account-disjoint test set is needed for a credible generalization estimate.
