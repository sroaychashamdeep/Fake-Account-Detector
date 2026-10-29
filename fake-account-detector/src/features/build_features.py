"""Feature engineering and a trainable scikit-learn preprocessing pipeline."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


NUMERIC_COLUMNS = [
    "statuses_count", "followers_count", "friends_count", "favourites_count",
    "listed_count", "default_profile", "default_profile_image", "geo_enabled",
    "profile_use_background_image", "profile_background_tile", "protected",
    "verified", "utc_offset",
]
CATEGORICAL_COLUMNS = [
    "lang", "time_zone", "profile_text_color", "profile_sidebar_border_color",
    "profile_sidebar_fill_color", "profile_background_color", "profile_link_color",
]
REQUIRED_INPUT_COLUMNS = [
    "statuses_count", "followers_count", "friends_count", "favourites_count",
    "listed_count",
]


class AccountFeatureBuilder(BaseEstimator, TransformerMixin):
    """Select account statistics and profile attributes while excluding identifiers."""

    def fit(self, X: pd.DataFrame, y: Any = None) -> "AccountFeatureBuilder":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        frame = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)
        out = pd.DataFrame(index=frame.index)
        for column in NUMERIC_COLUMNS:
            values = pd.to_numeric(frame[column], errors="coerce") if column in frame else np.nan
            out[column] = values
        for column in CATEGORICAL_COLUMNS:
            values = frame[column].astype("string") if column in frame else pd.Series(pd.NA, index=frame.index, dtype="string")
            values = values.str.strip().replace("", pd.NA)
            # scikit-learn imputers expect ordinary Python missing values, not pd.NA.
            out[column] = values.astype(object).where(values.notna(), np.nan)
        return out[NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
        ("scaler", StandardScaler()),
    ])
    categorical = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value="__MISSING__", keep_empty_features=True)),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric, NUMERIC_COLUMNS),
        ("categorical", categorical, CATEGORICAL_COLUMNS),
    ], remainder="drop")


def build_feature_pipeline(classifier: Any) -> Pipeline:
    """Return one serializable pipeline for fit, validation, and prediction."""
    return Pipeline([
        ("features", AccountFeatureBuilder()),
        ("preprocess", build_preprocessor()),
        ("classifier", classifier),
    ])
