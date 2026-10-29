"""Prediction helpers for CSV and Excel account data."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.features.build_features import REQUIRED_INPUT_COLUMNS


def predict_file(model_path: str | Path, input_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    """Preserve input columns and append predictions to a new Excel workbook."""
    source, destination = Path(input_path), Path(output_path)
    if not source.is_file():
        raise FileNotFoundError(f"Prediction input file not found: {source}")
    if destination.suffix.casefold() != ".xlsx":
        raise ValueError("Prediction output must be a new .xlsx file")
    extension = source.suffix.casefold()
    if extension == ".csv":
        frame = pd.read_csv(source)
    elif extension in {".xlsx", ".xls"}:
        frame = pd.read_excel(source)
    else:
        raise ValueError("Prediction input must be a .csv, .xlsx, or .xls file")
    missing = sorted(set(REQUIRED_INPUT_COLUMNS) - set(frame.columns))
    if missing:
        raise ValueError(f"Input has an incompatible schema; missing required features: {missing}")
    features = frame.drop(columns=["is_fake"]) if "is_fake" in frame else frame
    model = joblib.load(model_path)
    labels = model.predict(features)
    output = frame.copy()
    output["predicted_is_fake"] = labels.astype(int)
    if hasattr(model, "predict_proba"):
        output["fake_probability"] = model.predict_proba(features)[:, 1]
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_excel(destination, index=False)
    return output
