"""Compare baseline classifiers using only a stratified training validation split."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

from src.data.load_data import TARGET, load_training_data
from src.evaluation.metrics import calculate_metrics
from src.features.build_features import REQUIRED_INPUT_COLUMNS, build_feature_pipeline


EXCLUDED_COLUMNS = {
    TARGET, "id", "name", "screen_name", "url", "profile_image_url",
    "profile_image_url_https", "profile_banner_url",
    "profile_background_image_url", "profile_background_image_url_https",
    "description", "location", "created_at", "updated", "dataset", "RAND", "random_order",
}


def _classifiers(seed: int) -> dict[str, Any]:
    return {
        "dummy": DummyClassifier(strategy="most_frequent"),
        "logistic_regression": LogisticRegression(
            max_iter=2000, class_weight="balanced", random_state=seed,
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=400, min_samples_leaf=2, class_weight="balanced_subsample",
            n_jobs=-1, random_state=seed,
        ),
    }


def train_and_select(
    fake_path: str | Path,
    real_path: str | Path,
    model_path: str | Path,
    results_path: str | Path,
    seed: int = 42,
    validation_size: float = 0.2,
) -> dict[str, Any]:
    """Select on a held-out validation split, then refit the selected pipeline."""
    data = load_training_data(fake_path, real_path)
    missing = sorted(set(REQUIRED_INPUT_COLUMNS) - set(data.columns))
    if missing:
        raise ValueError(f"Training data missing core account statistics: {missing}")
    feature_columns = [c for c in data.columns if c not in EXCLUDED_COLUMNS]
    X, y = data[feature_columns], data[TARGET]
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=validation_size, random_state=seed, stratify=y,
    )
    comparisons: dict[str, Any] = {}
    fitted: dict[str, Any] = {}
    for name, classifier in _classifiers(seed).items():
        pipeline = build_feature_pipeline(classifier)
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_val)
        probabilities = pipeline.predict_proba(X_val)[:, 1] if hasattr(pipeline, "predict_proba") else None
        comparisons[name] = calculate_metrics(y_val, predictions, probabilities)
        fitted[name] = pipeline
    selected = max(
        comparisons,
        key=lambda name: (
            comparisons[name].get("f1_fake", 0),
            comparisons[name].get("roc_auc", 0),
            comparisons[name].get("accuracy", 0),
        ),
    )
    final_pipeline = build_feature_pipeline(_classifiers(seed)[selected])
    final_pipeline.fit(X, y)
    model_destination, results_destination = Path(model_path), Path(results_path)
    model_destination.parent.mkdir(parents=True, exist_ok=True)
    results_destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(final_pipeline, model_destination)
    result = {
        "selection_basis": "stratified validation split from combined training sources; test file not used",
        "seed": seed,
        "validation_size": validation_size,
        "training_rows_after_validation_cleanup": int(len(data)),
        "feature_columns_passed_to_pipeline": feature_columns,
        "excluded_columns": sorted(EXCLUDED_COLUMNS),
        "validation_results": comparisons,
        "selected_model": selected,
        "saved_pipeline": str(model_destination),
    }
    results_destination.write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
