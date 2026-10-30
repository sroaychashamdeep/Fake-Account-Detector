"""Feature engineering and a trainable scikit-learn preprocessing pipeline."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

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

METADATA_NUMERIC_COLUMNS = [
    "has_profile_banner",
    "has_external_url",
    "has_description",
    "description_length",
    "description_digits_count",
    "has_location",
    "screen_name_length",
    "screen_name_digits_count",
    "screen_name_digits_ratio",
    "name_length",
    "name_digits_count",
    "name_eq_screen_name",
    "account_age_days",
    "statuses_per_day",
    "followers_per_day",
    "friends_per_day",
]

ALL_NUMERIC_COLUMNS = BASE_NUMERIC_COLUMNS + ENGINEERED_NUMERIC_COLUMNS + METADATA_NUMERIC_COLUMNS

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
    "bio": "description",
    "biography": "description",
    "username": "screen_name",
    "user_name": "screen_name",
    "handle": "screen_name",
    "full_name": "name",
    "display_name": "name",
    "website": "url",
    "external_url": "url",
    "banner": "profile_banner_url",
    "header_image": "profile_banner_url",
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

        # Profile metadata signals
        if "profile_banner_url" in frame:
            out["has_profile_banner"] = frame["profile_banner_url"].notna().astype(float)
        else:
            out["has_profile_banner"] = np.nan

        if "url" in frame:
            url_str = frame["url"].astype(str).str.strip().str.lower()
            out["has_external_url"] = (~frame["url"].isna() & ~url_str.isin(["0", "nan", "none", "", "false"])).astype(float)
        else:
            out["has_external_url"] = np.nan

        if "description" in frame:
            desc = frame["description"].fillna("").astype(str)
            out["has_description"] = (desc.str.strip().str.len() > 0).astype(float)
            out["description_length"] = desc.str.len().astype(float)
            out["description_digits_count"] = desc.str.count(r"\d").astype(float)
        else:
            out["has_description"] = np.nan
            out["description_length"] = np.nan
            out["description_digits_count"] = np.nan

        if "location" in frame:
            loc = frame["location"].fillna("").astype(str)
            out["has_location"] = (loc.str.strip().str.len() > 0).astype(float)
        else:
            out["has_location"] = np.nan

        # Screen name & Display name forensic signals
        if "screen_name" in frame:
            sn = frame["screen_name"].fillna("").astype(str)
            out["screen_name_length"] = sn.str.len().astype(float)
            digits = sn.str.count(r"\d").astype(float)
            out["screen_name_digits_count"] = digits
            out["screen_name_digits_ratio"] = digits / (out["screen_name_length"] + 1.0)
        else:
            sn = pd.Series("", index=frame.index)
            out["screen_name_length"] = np.nan
            out["screen_name_digits_count"] = np.nan
            out["screen_name_digits_ratio"] = np.nan

        if "name" in frame:
            nm = frame["name"].fillna("").astype(str)
            out["name_length"] = nm.str.len().astype(float)
            out["name_digits_count"] = nm.str.count(r"\d").astype(float)
            out["name_eq_screen_name"] = (nm.str.lower() == sn.str.lower()).astype(float)
        else:
            out["name_length"] = np.nan
            out["name_digits_count"] = np.nan
            out["name_eq_screen_name"] = np.nan

        # Account creation age & publishing velocity
        if "created_at" in frame:
            dates = pd.to_datetime(frame["created_at"], format="%a %b %d %H:%M:%S +0000 %Y", errors="coerce")
            ref_date = pd.Timestamp("2016-01-01")
            age_days = (ref_date - dates).dt.total_seconds() / (24 * 3600)
            out["account_age_days"] = age_days.clip(lower=1)
            out["statuses_per_day"] = statuses / (out["account_age_days"] + 1.0)
            out["followers_per_day"] = followers / (out["account_age_days"] + 1.0)
            out["friends_per_day"] = friends / (out["account_age_days"] + 1.0)
        else:
            out["account_age_days"] = np.nan
            out["statuses_per_day"] = np.nan
            out["followers_per_day"] = np.nan
            out["friends_per_day"] = np.nan

        # Categoricals
        for column in CATEGORICAL_COLUMNS:
            values = frame[column].astype("string") if column in frame else pd.Series(pd.NA, index=frame.index, dtype="string")
            values = values.str.strip().replace("", pd.NA)
            out[column] = values.astype(object).where(values.notna(), np.nan)

        return out[ALL_NUMERIC_COLUMNS + CATEGORICAL_COLUMNS]


def build_preprocessor() -> ColumnTransformer:
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median", add_indicator=True, keep_empty_features=True)),
        ("scaler", RobustScaler()),
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
