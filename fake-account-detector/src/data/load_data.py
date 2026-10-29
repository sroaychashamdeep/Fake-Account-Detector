"""Read the three approved workbooks and validate their labels and schemas."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


TARGET = "is_fake"


def load_workbook(path: str | Path) -> pd.DataFrame:
    """Load the first worksheet from an Excel workbook with a useful error."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(f"Workbook not found: {source}")
    try:
        return pd.read_excel(source)
    except Exception as exc:
        raise ValueError(f"Could not read workbook {source}: {exc}") from exc


def _validate_class_file(frame: pd.DataFrame, expected: int, source: str) -> pd.DataFrame:
    frame = frame.copy()
    if TARGET not in frame:
        frame[TARGET] = expected
        return frame
    labels = pd.to_numeric(frame[TARGET], errors="coerce")
    valid = labels.isin([0, 1])
    contradictory = valid & labels.ne(expected)
    if contradictory.any():
        raise ValueError(
            f"{source} contains {int(contradictory.sum())} labels that conflict with "
            f"its declared class {expected}; labels were not overwritten."
        )
    frame[TARGET] = labels.where(valid)
    return frame


def load_training_data(fake_path: str | Path, real_path: str | Path) -> pd.DataFrame:
    """Combine compatible fake/real sources and reproducibly shuffle valid labels."""
    fake = _validate_class_file(load_workbook(fake_path), 1, str(fake_path))
    real = _validate_class_file(load_workbook(real_path), 0, str(real_path))
    fake_columns, real_columns = set(fake.columns), set(real.columns)
    if fake_columns != real_columns:
        raise ValueError(
            "Training workbook schemas differ. "
            f"Only in fake: {sorted(fake_columns - real_columns)}; "
            f"only in real: {sorted(real_columns - fake_columns)}"
        )
    columns = list(fake.columns)
    data = pd.concat([fake[columns], real[columns]], ignore_index=True)
    data[TARGET] = pd.to_numeric(data[TARGET], errors="coerce")
    data = data.loc[data[TARGET].isin([0, 1])].copy()
    data[TARGET] = data[TARGET].astype("int8")
    # Exact duplicate records can artificially weight the model.
    data = data.drop_duplicates().reset_index(drop=True)
    return data.sample(frac=1, random_state=42).reset_index(drop=True)


def validate_feature_schema(frame: pd.DataFrame, required: Iterable[str]) -> None:
    """Raise a readable error when essential prediction-time fields are absent."""
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"Input is missing required account feature columns: {missing}")
