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

BASE_NUMERIC_COLUMNS = [
    "statuses_count", "followers_count", "friends_count", "favourites_count",
    "listed_count", "default_profile", "default_profile_image", "geo_enabled",
    "profile_use_background_image", "profile_background_tile", "protected",
    "verified", "utc_offset",
]

ENGINEERED_NUMERIC_COLUMNS = [
    "follower_friend_ratio",
    "friend_follower_ratio",
    "reputation_score",
    "engagement_rate",
    "status_to_follower",
    "listed_to_follower",
    "log_followers",
    "log_friends",
    "log_statuses",
    "log_favourites",
    "log_follower_diff",
    "default_combo",
    "zero_favourites",
    "zero_statuses",
    "high_following_low_followers",
]

ALL_NUMERIC_COLUMNS = BASE_NUMERIC_COLUMNS + ENGINEERED_NUMERIC_COLUMNS

CATEGORICAL_COLUMNS = [
    "lang", "time_zone", "profile_text_color", "profile_sidebar_border_color",
    "profile_sidebar_fill_color", "profile_background_color", "profile_link_color",
]

REQUIRED_INPUT_COLUMNS = [
    "statuses_count", "followers_count", "friends_count", "favourites_count",
    "listed_count",
]

COLUMN_NORMALIZATION_MAP = {
    "followers": "followers_count",
    "follower": "followers_count",
    "follower_count": "followers_count",
    "following": "friends_count",
    "followings": "friends_count",
    "friends": "friends_count",
    "friend_count": "friends_count",
    "statuses": "statuses_count",
    "posts": "statuses_count",
    "post_count": "statuses_count",
    "tweets": "statuses_count",
    "tweet_count": "statuses_count",
    "favourites": "favourites_count",
    "favorites": "favourites_count",
    "likes": "favourites_count",
    "like_count": "favourites_count",
    "listed": "listed_count",
    "lists": "listed_count",
    "list_count": "listed_count",
    "default_avatar": "default_profile_image",
    "default_theme": "default_profile",
    "is_private": "protected",
    "private": "protected",
    "language": "lang",
}


class AccountFeatureBuilder(BaseEstimator, TransformerMixin):
    """Normalize input columns, extract baseline attributes, and compute forensic engagement ratios."""

    def fit(self, X: pd.DataFrame, y: Any = None) -> "AccountFeatureBuilder":
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        frame = X.copy() if isinstance(X, pd.DataFrame) else pd.DataFrame(X)

        # Normalize column aliases for resilient batch and single input handling
        normalized_cols = {
            c: COLUMN_NORMALIZATION_MAP.get(
                str(c).strip().lower().replace(" ", "_"),
                str(c).strip().lower().replace(" ", "_")
            )
            for c in frame.columns
        }
        frame = frame.rename(columns=normalized_cols)

        out = pd.DataFrame(index=frame.index)

        # Base numericals
        for column in BASE_NUMERIC_COLUMNS:
            values = pd.to_numeric(frame[column], errors="coerce") if column in frame else np.nan
            out[column] = values

        followers = out["followers_count"].fillna(0).clip(lower=0)
        friends = out["friends_count"].fillna(0).clip(lower=0)
        statuses = out["statuses_count"].fillna(0).clip(lower=0)
        favourites = out["favourites_count"].fillna(0).clip(lower=0)
        listed = out["listed_count"].fillna(0).clip(lower=0)
        default_p = out["default_profile"].fillna(0)
        default_img = out["default_profile_image"].fillna(0)

        # Domain engineered behavioral features
        out["follower_friend_ratio"] = followers / (friends + 1.0)
        out["friend_follower_ratio"] = friends / (followers + 1.0)
        out["reputation_score"] = followers / (followers + friends + 1.0)
        out["engagement_rate"] = favourites / (statuses + 1.0)
        out["status_to_follower"] = statuses / (followers + 1.0)
        out["listed_to_follower"] = listed / (followers + 1.0)

        # Power-law log transforms
        out["log_followers"] = np.log1p(followers)
        out["log_friends"] = np.log1p(friends)
        out["log_statuses"] = np.log1p(statuses)
        out["log_favourites"] = np.log1p(favourites)
        out["log_follower_diff"] = out["log_followers"] - out["log_friends"]

        # Behavioral flags & heuristics
        out["default_combo"] = default_p * default_img
        out["zero_favourites"] = (favourites == 0).astype(float)
        out["zero_statuses"] = (statuses == 0).astype(float)
        out["high_following_low_followers"] = ((friends > 500) & (out["follower_friend_ratio"] < 0.05)).astype(float)

        # Categoricals
        for column in CATEGORICAL_COLUMNS:
            values = frame[column].astype("string") if column in frame else pd.Series(pd.NA, index=frame.index, dtype="string")
            values = values.str.strip().replace("", pd.NA)
            out[column] = values.astype(object).where(values.notna(), np.nan)

        return out[ALL_NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]


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
        ("numeric", numeric, ALL_NUMERIC_COLUMNS),
        ("categorical", categorical, CATEGORICAL_COLUMNS),
    ], remainder="drop")


def build_feature_pipeline(classifier: Any) -> Pipeline:
    """Return one serializable pipeline for fit, validation, and prediction."""
    return Pipeline([
        ("features", AccountFeatureBuilder()),
        ("preprocess", build_preprocessor()),
        ("classifier", classifier),
    ])
