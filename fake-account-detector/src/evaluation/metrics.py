"""Evaluation metrics and leakage/overlap diagnostics."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, average_precision_score, classification_report,
    confusion_matrix, f1_score, precision_score, recall_score, roc_auc_score,
)


def calculate_metrics(y_true: Any, y_pred: Any, probabilities: Any | None = None) -> dict[str, Any]:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    result: dict[str, Any] = {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision_fake": float(precision_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "recall_fake": float(recall_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "f1_fake": float(f1_score(y_true, y_pred, pos_label=1, zero_division=0)),
        "confusion_matrix_labels_0_1": matrix.tolist(),
        "classification_report": classification_report(
            y_true, y_pred, labels=[0, 1], target_names=["real (0)", "fake (1)"],
            output_dict=True, zero_division=0,
        ),
    }
    if probabilities is not None and len(np.unique(y_true)) == 2:
        result["roc_auc"] = float(roc_auc_score(y_true, probabilities))
        result["pr_auc_average_precision"] = float(average_precision_score(y_true, probabilities))
    return result


def overlap_diagnostics(training: pd.DataFrame, testing: pd.DataFrame) -> dict[str, Any]:
    """Count exact shared rows and overlap on fields that can identify accounts."""
    result: dict[str, Any] = {"exact_record_overlap": 0, "identity_overlap": {}}
    shared = [c for c in training.columns if c in testing.columns and c != "RAND"]
    def row_keys(frame: pd.DataFrame) -> set[tuple[str, ...]]:
        values = frame[shared].astype("string").fillna("<NA>")
        return set(map(tuple, values.to_numpy().tolist()))
    result["exact_record_overlap"] = len(row_keys(training) & row_keys(testing))
    for column in ["screen_name", "profile_image_url_https", "profile_image_url", "name"]:
        if column not in training or column not in testing:
            continue
        normalize = lambda s: set(s.dropna().astype(str).str.strip().str.casefold()) - {"", "0", "0.0"}
        train_values, test_values = normalize(training[column]), normalize(testing[column])
        overlap = test_values & train_values
        result["identity_overlap"][column] = {
            "unique_test_values": len(test_values),
            "unique_values_overlapping_training": len(overlap),
            "test_rows_with_training_value": int(
                testing[column].astype("string").str.strip().str.casefold().isin(train_values).sum()
            ),
        }
    return result
