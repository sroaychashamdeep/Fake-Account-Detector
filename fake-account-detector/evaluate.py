"""Evaluate the selected, already-fitted model once on the labeled test workbook."""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from sklearn.metrics import ConfusionMatrixDisplay

from src.data.load_data import TARGET, load_training_data, load_workbook
from src.evaluation.metrics import calculate_metrics, overlap_diagnostics
from src.models.train_model import EXCLUDED_COLUMNS


def main() -> None:
    root = Path(__file__).resolve().parent
    config = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8"))
    test_path = root / config["data"]["test"]
    test = load_workbook(test_path)
    if TARGET not in test:
        raise ValueError(f"Final test workbook has no ground-truth {TARGET} column")
    labels = pd.to_numeric(test[TARGET], errors="coerce")
    if labels.isna().any() or not labels.isin([0, 1]).all():
        raise ValueError("Final test labels must all be valid 0/1 values")
    training = load_training_data(root / config["data"]["fake_train"], root / config["data"]["real_train"])
    overlap = overlap_diagnostics(training, test)
    feature_columns = [c for c in test.columns if c not in EXCLUDED_COLUMNS]
    model = joblib.load(root / config["model"]["artifact"])
    selection_path = root / config["model"]["selection_results"]
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    X_test, y_test = test[feature_columns], labels.astype(int)
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)[:, 1] if hasattr(model, "predict_proba") else None
    metrics = calculate_metrics(y_test, predictions, probabilities)
    metrics.update({
        "test_rows": int(len(test)),
        "test_label_distribution": {str(k): int(v) for k, v in y_test.value_counts().items()},
        "overlap_diagnostics": overlap,
        "independence_warning": (
            "This test set is contaminated by shared records and account identifiers; "
            "metrics are descriptive and do not establish independent generalization."
        ),
        "false_positives_real_predicted_fake": int(((y_test == 0) & (predictions == 1)).sum()),
        "false_negatives_fake_predicted_real": int(((y_test == 1) & (predictions == 0)).sum()),
        "used_for_model_selection": False,
        "selected_model": selection["selected_model"],
        "selection_results_file": str(selection_path.relative_to(root)),
        "pipeline_file": config["model"]["artifact"],
    })
    results_path = root / config["model"]["results"]
    results_path.parent.mkdir(parents=True, exist_ok=True)
    results_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    plot_path = root / config["model"]["metrics_plot"]
    plot_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(5.5, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_test, predictions, labels=[0, 1], display_labels=["Real (0)", "Fake (1)"],
        cmap="Blues", ax=ax, colorbar=False,
    )
    ax.set_title("Final test confusion matrix\n(overlapping records; interpret cautiously)")
    fig.tight_layout()
    fig.savefig(plot_path, dpi=160)
    plt.close(fig)
    print(json.dumps({k: metrics[k] for k in ["accuracy", "precision_fake", "recall_fake", "f1_fake", "roc_auc", "pr_auc_average_precision", "confusion_matrix_labels_0_1", "false_positives_real_predicted_fake", "false_negatives_fake_predicted_real"]}, indent=2))
    print(f"Class report: {json.dumps(metrics['classification_report'], indent=2)}")
    print(f"Overlap diagnostics: {json.dumps(overlap, indent=2)}")
    print("WARNING: test metrics are descriptive because records/accounts overlap training.")


if __name__ == "__main__":
    main()
