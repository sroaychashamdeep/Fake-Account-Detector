"""Cleaning helpers that never alter the original source workbooks."""
from __future__ import annotations

import pandas as pd


def label_distribution(frame: pd.DataFrame, target: str = "is_fake") -> dict[str, int]:
    if target not in frame:
        return {}
    counts = frame[target].value_counts(dropna=False)
    return {str(label): int(count) for label, count in counts.items()}


def duplicate_summary(frame: pd.DataFrame, identifiers: tuple[str, ...] = (
    "id", "screen_name", "profile_image_url_https", "profile_image_url"
)) -> dict[str, int]:
    result = {"exact_rows": int(frame.duplicated().sum())}
    for column in identifiers:
        if column in frame:
            values = frame[column].dropna().astype(str).str.strip().str.casefold()
            # Empty strings and zero-valued placeholder IDs are not useful keys.
            values = values[values.ne("") & values.ne("0") & values.ne("0.0")]
            result[f"duplicate_{column}"] = int(values.duplicated().sum())
    return result
