import io
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Ensure root directory is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from app import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert "model_type" in data

def test_predict_endpoint_authentic():
    payload = {
        "followers_count": 1500,
        "friends_count": 350,
        "statuses_count": 800,
        "favourites_count": 1200,
        "listed_count": 10,
        "default_profile": 0,
        "default_profile_image": 0,
        "geo_enabled": 1,
        "verified": 0,
        "protected": 0,
        "lang": "en"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_fake"] in {0, 1}
    assert "fake_probability" in data
    assert "real_probability" in data
    assert "risk_level" in data
    assert "flags" in data

def test_predict_endpoint_bot():
    payload = {
        "followers_count": 12,
        "friends_count": 3500,
        "statuses_count": 2,
        "favourites_count": 0,
        "listed_count": 0,
        "default_profile": 1,
        "default_profile_image": 1,
        "geo_enabled": 0,
        "verified": 0,
        "protected": 0,
        "lang": "en"
    }
    res = client.post("/api/predict", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["is_fake"] == 1
    assert data["fake_probability"] > 50.0

def test_batch_predict_csv():
    csv_content = b"followers,following,posts,likes,default_avatar\n100,200,50,30,0\n5,2500,1,0,1\n"
    res = client.post(
        "/api/batch-predict",
        files={"file": ("test.csv", io.BytesIO(csv_content), "text/csv")}
    )
    assert res.status_code == 200
    data = res.json()
    assert data["total_accounts"] == 2
    assert "detected_fake" in data
    assert "detected_real" in data
    assert len(data["sample_results"]) == 2

def test_index_html():
    res = client.get("/")
    assert res.status_code == 200
    assert "VeriProfile AI" in res.text
