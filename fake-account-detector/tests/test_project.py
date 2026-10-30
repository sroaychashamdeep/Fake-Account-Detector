from __future__ import annotations

import pandas as pd
import pytest
import numpy as np

from src.data.load_data import load_training_data, validate_feature_schema
from src.features.build_features import (
    AccountFeatureBuilder, REQUIRED_INPUT_COLUMNS,
    ALL_NUMERIC_COLUMNS, ENGINEERED_NUMERIC_COLUMNS
)
from src.models.predict_model import predict_file
from src.models.train_model import train_and_select


def sample_frame(label: int, count: int = 12) -> pd.DataFrame:
    rows = []
    for index in range(count):
        rows.append({
            "statuses_count": index + label * 5,
            "followers_count": index + label * 30,
            "friends_count": index + label,
            "favourites_count": index * 2,
            "listed_count": index // 2,
            "is_fake": label,
            "dataset": "INT" if label else "E13",
        })
    return pd.DataFrame(rows)


def test_training_loader_validates_schema_labels_and_shuffles(tmp_path):
    fake_path, real_path = tmp_path / "fake.xlsx", tmp_path / "real.xlsx"
    sample_frame(1).to_excel(fake_path, index=False)
    sample_frame(0).to_excel(real_path, index=False)
    combined = load_training_data(fake_path, real_path)
    assert len(combined) == 24
    assert set(combined.is_fake) == {0, 1}
    assert "dataset" in combined
    validate_feature_schema(combined, REQUIRED_INPUT_COLUMNS)
    with pytest.raises(ValueError, match="schemas differ"):
        other = sample_frame(0).drop(columns="friends_count")
        other.to_excel(real_path, index=False)
        load_training_data(fake_path, real_path)


def test_feature_builder_handles_optional_and_malformed_values():
    frame = pd.DataFrame({
        "statuses_count": ["12", "not-a-number"],
        "followers_count": [1, 2],
        "friends_count": [1, 2],
        "favourites_count": [0, 0],
        "listed_count": [0, 0],
        "created_at": ["bad timestamp", None],
        "updated": ["2015-02-14", None],
    })
    features = AccountFeatureBuilder().fit_transform(frame)
    assert features.loc[0, "statuses_count"] == 12
    assert pd.isna(features.loc[1, "statuses_count"])
    assert "account_age_days" in features and pd.isna(features.loc[0, "account_age_days"])
    assert "lang" in features and features["lang"].isna().all()
    # Check that all engineered features are present
    for col in ENGINEERED_NUMERIC_COLUMNS:
        assert col in features.columns


def test_feature_builder_column_normalization():
    # User provides non-standard column headers
    user_frame = pd.DataFrame({
        "Followers": [1000],
        "Following": [250],
        "Posts": [400],
        "Likes": [800],
        "Listed": [5],
        "Default Avatar": [0],
        "Default Theme": [0],
    })
    features = AccountFeatureBuilder().fit_transform(user_frame)
    assert features.loc[0, "followers_count"] == 1000
    assert features.loc[0, "friends_count"] == 250
    assert features.loc[0, "statuses_count"] == 400
    assert features.loc[0, "favourites_count"] == 800
    assert features.loc[0, "listed_count"] == 5
    # Verify calculated ratios
    expected_ratio = 1000 / (250 + 1.0)
    assert np.isclose(features.loc[0, "follower_friend_ratio"], expected_ratio)


def test_feature_builder_zero_division_safety():
    # Accounts with zeroes across the board
    zero_frame = pd.DataFrame([{
        "followers_count": 0,
        "friends_count": 0,
        "statuses_count": 0,
        "favourites_count": 0,
        "listed_count": 0,
    }])
    features = AccountFeatureBuilder().fit_transform(zero_frame)
    assert not features["follower_friend_ratio"].isna().any()
    assert not np.isinf(features["follower_friend_ratio"]).any()
    assert features.loc[0, "follower_friend_ratio"] == 0.0
    assert features.loc[0, "reputation_score"] == 0.0
    assert features.loc[0, "zero_favourites"] == 1.0
    assert features.loc[0, "zero_statuses"] == 1.0


def test_training_and_prediction_share_pipeline_and_preserve_input(tmp_path):
    fake_path, real_path = tmp_path / "fake.xlsx", tmp_path / "real.xlsx"
    sample_frame(1).to_excel(fake_path, index=False)
    sample_frame(0).to_excel(real_path, index=False)
    model_path, result_path = tmp_path / "pipeline.joblib", tmp_path / "selection.json"
    results = train_and_select(fake_path, real_path, model_path, result_path, seed=11, validation_size=0.25)
    assert results["selected_model"] in {"dummy", "logistic_regression", "random_forest"}
    assert "dataset" not in results["feature_columns_passed_to_pipeline"]
    input_path, output_path = tmp_path / "new.csv", tmp_path / "predictions.xlsx"
    new_rows = sample_frame(0, 2)
    new_rows.to_csv(input_path, index=False)
    predicted = predict_file(model_path, input_path, output_path)
    assert output_path.is_file()
    assert len(predicted) == 2
    assert "predicted_is_fake" in predicted
    assert "fake_probability" in predicted
    assert "is_fake" in predicted
    assert predicted["is_fake"].tolist() == new_rows["is_fake"].tolist()
    assert "dataset" in predicted
    assert list(pd.read_excel(output_path).columns) == list(predicted.columns)
    with pytest.raises(ValueError, match="missing required features"):
        bad_input = tmp_path / "bad.csv"
        new_rows.drop(columns="followers_count").to_csv(bad_input, index=False)
        predict_file(model_path, bad_input, tmp_path / "bad-output.xlsx")
