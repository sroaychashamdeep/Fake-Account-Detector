import os
import sys
from pathlib import Path
from typing import Optional, List, Dict, Any
from decimal import Decimal
import io
import json

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import pandas as pd

# Safe local environment loading
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except Exception:
    pass

# Ensure fake-account-detector source is on sys.path
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "fake-account-detector"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

# Pipeline path
MODEL_PATH = PROJECT_DIR / "models" / "fake_account_pipeline.joblib"

app = FastAPI(
    title="Fake Account Detector AI",
    description="Machine Learning Web Interface for detecting fake social media profiles",
    version="1.2.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load ML pipeline
pipeline = None

def get_pipeline():
    global pipeline
    if pipeline is None:
        if not MODEL_PATH.exists():
            raise RuntimeError(f"Model file not found at {MODEL_PATH}")
        pipeline = joblib.load(MODEL_PATH)
    return pipeline

class AccountInput(BaseModel):
    # Core numerical inputs
    statuses_count: float = Field(default=100.0, description="Number of tweets/posts published", ge=0)
    followers_count: float = Field(default=250.0, description="Number of followers", ge=0)
    friends_count: float = Field(default=300.0, description="Number of accounts followed (following)", ge=0)
    favourites_count: float = Field(default=150.0, description="Number of likes / favourites given", ge=0)
    listed_count: float = Field(default=2.0, description="Number of public lists account belongs to", ge=0)

    # Boolean flags (0 or 1)
    default_profile: int = Field(default=0, description="1 if default theme is active, else 0")
    default_profile_image: int = Field(default=0, description="1 if default avatar/egg image is active, else 0")
    geo_enabled: int = Field(default=1, description="1 if geolocation is enabled, else 0")
    verified: int = Field(default=0, description="1 if account is verified, else 0")
    protected: int = Field(default=0, description="1 if account is private/protected, else 0")
    profile_use_background_image: int = Field(default=1, description="1 if profile uses background image, else 0")
    profile_background_tile: int = Field(default=0, description="1 if profile background is tiled, else 0")

    # Optional metadata
    lang: Optional[str] = Field(default="en", description="Language code (e.g., en, it, es)")
    time_zone: Optional[str] = Field(default=None, description="Timezone string")
    utc_offset: Optional[float] = Field(default=0.0, description="UTC offset in seconds")


def evaluate_behavioral_flags(data: Dict[str, Any], fake_prob: float) -> List[Dict[str, str]]:
    flags = []
    
    # Safe float conversions preventing TypeErrors on dirty string inputs
    followers = float(pd.to_numeric(data.get("followers_count", 0), errors="coerce") or 0)
    friends = float(pd.to_numeric(data.get("friends_count", 0), errors="coerce") or 0)
    statuses = float(pd.to_numeric(data.get("statuses_count", 0), errors="coerce") or 0)
    favourites = float(pd.to_numeric(data.get("favourites_count", 0), errors="coerce") or 0)
    default_img = int(pd.to_numeric(data.get("default_profile_image", 0), errors="coerce") or 0)
    default_prof = int(pd.to_numeric(data.get("default_profile", 0), errors="coerce") or 0)
    verified = int(pd.to_numeric(data.get("verified", 0), errors="coerce") or 0)

    # Ratio analysis
    ratio = followers / max(friends, 1.0)
    if friends > 500 and ratio < 0.05:
        flags.append({
            "type": "danger",
            "title": "Severe Follower-Following Imbalance",
            "desc": f"Account follows {int(friends)} users but only has {int(followers)} followers (ratio {ratio:.3f}). Classic follow-churn pattern."
        })
    elif ratio > 1.5:
        flags.append({
            "type": "success",
            "title": "Healthy Follower Ratio",
            "desc": f"More followers ({int(followers):,}) than followed accounts ({int(friends):,})."
        })

    # Avatar check
    if default_img == 1:
        flags.append({
            "type": "danger",
            "title": "Default Profile Picture",
            "desc": "Using the default silhouette avatar/egg picture without custom branding."
        })
    else:
        flags.append({
            "type": "success",
            "title": "Custom Profile Picture",
            "desc": "Account has uploaded a personalized profile image."
        })

    # Activity & Engagement
    if statuses < 10 and friends > 200:
        flags.append({
            "type": "warning",
            "title": "High Following, Minimal Content",
            "desc": f"Account has posted only {int(statuses)} times despite actively following {int(friends)} accounts."
        })
    elif statuses > 1000:
        flags.append({
            "type": "info",
            "title": "Established Posting History",
            "desc": f"Account has a substantial history of {int(statuses):,} posts."
        })

    if favourites == 0 and statuses > 20:
        flags.append({
            "type": "warning",
            "title": "Zero Engagement Behavior",
            "desc": "Account has never liked or favourited any posts, typical of automated broadcasting bots."
        })

    # Verified check
    if verified == 1:
        flags.append({
            "type": "success",
            "title": "Verified Account Badge",
            "desc": "Account holds verified status."
        })

    return flags


@app.post("/api/predict")
def predict_account(account: AccountInput):
    model = get_pipeline()
    row = account.model_dump()
    df = pd.DataFrame([row])

    try:
        pred = int(model.predict(df)[0])
        probs = model.predict_proba(df)[0]
        real_prob = float(probs[0])
        fake_prob = float(probs[1])

        # Risk classification
        if fake_prob >= 0.75:
            risk_level = "Critical / High Risk"
            verdict = "Fake / Automated Bot"
        elif fake_prob >= 0.45:
            risk_level = "Moderate / Suspicious"
            verdict = "Suspicious Profile"
        elif fake_prob >= 0.20:
            risk_level = "Low Risk"
            verdict = "Likely Real Account"
        else:
            risk_level = "Minimal Risk"
            verdict = "Authentic Real Account"

        flags = evaluate_behavioral_flags(row, fake_prob)

        followers = float(row.get("followers_count", 0))
        friends = float(row.get("friends_count", 0))
        ff_ratio = round(followers / max(friends, 1.0), 3)

        return {
            "is_fake": pred,
            "verdict": verdict,
            "fake_probability": round(fake_prob * 100, 2),
            "real_probability": round(real_prob * 100, 2),
            "confidence": round(max(fake_prob, real_prob) * 100, 2),
            "risk_level": risk_level,
            "follower_following_ratio": ff_ratio,
            "flags": flags,
            "raw_scores": {
                "p_real": real_prob,
                "p_fake": fake_prob
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


class InstagramScanRequest(BaseModel):
    username: str = Field(..., description="Instagram username or profile URL", min_length=1)


@app.post("/api/scan-instagram")
def scan_instagram(req: InstagramScanRequest):
    token = os.getenv("APIFY_TOKEN")
    if not token:
        raise HTTPException(status_code=400, detail="APIFY_TOKEN not found in environment or .env file.")

    clean_user = req.username.strip().lstrip("@").replace("https://www.instagram.com/", "").replace("https://instagram.com/", "").strip("/").split("/")[0]
    if not clean_user:
        raise HTTPException(status_code=400, detail="Invalid username supplied.")

    try:
        from apify_client import ApifyClient
        client = ApifyClient(token=token)

        # Call apify/instagram-profile-scraper
        run = client.actor("apify/instagram-profile-scraper").call(
            run_input={"usernames": [clean_user]},
            max_total_charge_usd=Decimal("0.05")
        )

        dataset_id = getattr(run, "default_dataset_id", None) or (run.get("defaultDatasetId") if isinstance(run, dict) else None)
        if not dataset_id:
            raise HTTPException(status_code=500, detail="Apify run completed without a dataset ID.")

        items = client.dataset(dataset_id).list_items().items
        if not items:
            raise HTTPException(status_code=404, detail=f"No profile found for Instagram handle @{clean_user}")

        prof = items[0]
        followers = float(prof.get("followersCount") or 0)
        following = float(prof.get("followsCount") or 0)
        posts = float(prof.get("postsCount") or 0)
        verified = 1 if prof.get("verified") else 0
        protected = 1 if (prof.get("private") or prof.get("isPrivate")) else 0
        pic_url = prof.get("profilePicUrlHD") or prof.get("profilePicUrl") or ""
        default_img = 1 if ("default" in pic_url.lower() or not pic_url) else 0

        # Feed to AI pipeline
        model_input = {
            "statuses_count": posts,
            "followers_count": followers,
            "friends_count": following,
            "favourites_count": max(posts * 4.0, 15.0),
            "listed_count": 0.0,
            "default_profile": 0,
            "default_profile_image": default_img,
            "geo_enabled": 1,
            "verified": verified,
            "protected": protected,
            "profile_use_background_image": 1,
            "lang": "en"
        }

        model = get_pipeline()
        df = pd.DataFrame([model_input])
        pred = int(model.predict(df)[0])
        probs = model.predict_proba(df)[0]
        real_prob = float(probs[0])
        fake_prob = float(probs[1])

        if fake_prob >= 0.70:
            risk_level = "Critical / High Risk"
            verdict = "Fake / Automated Bot"
        elif fake_prob >= 0.40:
            risk_level = "Moderate / Suspicious"
            verdict = "Suspicious Profile"
        else:
            risk_level = "Minimal / Authentic"
            verdict = "Authentic Real User"

        flags = evaluate_behavioral_flags(model_input, fake_prob)
        ratio = round(followers / max(following, 1.0), 3)

        return {
            "profile": {
                "username": prof.get("username", clean_user),
                "full_name": prof.get("fullName", ""),
                "biography": prof.get("biography", ""),
                "profile_pic_url": pic_url,
                "followers_count": followers,
                "following_count": following,
                "posts_count": posts,
                "verified": bool(verified),
                "is_private": bool(protected),
                "external_url": prof.get("externalUrl") or (prof.get("externalUrls")[0] if isinstance(prof.get("externalUrls"), list) and prof.get("externalUrls") else None)
            },
            "analysis": {
                "is_fake": pred,
                "verdict": verdict,
                "fake_probability": round(fake_prob * 100, 2),
                "real_probability": round(real_prob * 100, 2),
                "confidence": round(max(fake_prob, real_prob) * 100, 2),
                "risk_level": risk_level,
                "follower_following_ratio": ratio,
                "flags": flags
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apify Instagram Scraper error: {str(e)}")


@app.post("/api/batch-predict")
async def batch_predict(file: UploadFile = File(...)):
    filename = (file.filename or "").lower()
    content = await file.read()

    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(io.BytesIO(content))
        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(io.BytesIO(content))
        else:
            raise HTTPException(status_code=400, detail="Only .csv and .xlsx files are supported.")

        # Clean empty rows
        df = df.dropna(how="all").reset_index(drop=True)
        if len(df) == 0:
            raise HTTPException(status_code=400, detail="Dataset contains no data rows.")

        model = get_pipeline()
        preds = model.predict(df)
        probs = model.predict_proba(df)

        df["ai_prediction"] = ["Fake" if p == 1 else "Real" for p in preds]
        df["fake_probability_%"] = np.round(probs[:, 1] * 100, 2)
        df["real_probability_%"] = np.round(probs[:, 0] * 100, 2)

        clean_sample = json.loads(df.head(20).to_json(orient="records", date_format="iso"))

        summary = {
            "total_accounts": len(df),
            "detected_fake": int((preds == 1).sum()),
            "detected_real": int((preds == 0).sum()),
            "fake_percentage": round(float((preds == 1).mean() * 100), 2),
            "sample_results": clean_sample
        }
        return JSONResponse(content=summary)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing error: {str(e)}")


@app.get("/api/health")
def health_check():
    pipe = get_pipeline()
    classifier = pipe.named_steps.get("classifier") if hasattr(pipe, "named_steps") else pipe
    return {
        "status": "healthy",
        "model_loaded": True,
        "model_type": type(classifier).__name__,
        "pipeline_path": str(MODEL_PATH)
    }


# Serve the main dashboard web interface
@app.get("/", response_class=HTMLResponse)
def index_page():
    index_file = BASE_DIR / "templates" / "index.html"
    if index_file.exists():
        return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Templates directory not ready</h1>")


if __name__ == "__main__":
    import uvicorn
    get_pipeline()
    print("Starting server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)
