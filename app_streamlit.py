import sys
from pathlib import Path
import streamlit as st
import pandas as pd
import joblib

# Ensure project source is accessible
BASE_DIR = Path(__file__).resolve().parent
PROJECT_DIR = BASE_DIR / "fake-account-detector"
sys.path.insert(0, str(PROJECT_DIR))

MODEL_PATH = PROJECT_DIR / "models" / "fake_account_pipeline.joblib"

st.set_page_config(
    page_title="Fake Account Detector AI",
    page_icon="🛡️",
    layout="wide"
)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

st.title("🛡️ Social Media Fake Account Detector AI")
st.markdown("Enter profile statistics to predict whether an account is **Authentic** or an **Automated Fake Bot**.")

model = load_model()

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📊 Profile Statistics")
    followers = st.number_input("Followers Count", min_value=0, value=250)
    friends = st.number_input("Following Count (Friends)", min_value=0, value=300)
    statuses = st.number_input("Tweets / Statuses Count", min_value=0, value=1200)
    favourites = st.number_input("Favourites / Likes Count", min_value=0, value=500)
    listed = st.number_input("Listed Count", min_value=0, value=3)

    st.subheader("⚙️ Profile Attributes")
    c1, c2 = st.columns(2)
    with c1:
        default_img = st.checkbox("Default Avatar (Egg/Silhouette)", value=False)
        default_profile = st.checkbox("Default Theme Uncustomized", value=False)
        verified = st.checkbox("Verified Account", value=False)
    with c2:
        geo = st.checkbox("Geolocation Enabled", value=True)
        header = st.checkbox("Custom Banner Image", value=True)
        protected = st.checkbox("Private / Protected Account", value=False)

    lang = st.selectbox("Language", ["en", "it", "es", "fr", "de"], index=0)

with col2:
    st.subheader("🔍 AI Diagnosis")
    
    input_data = pd.DataFrame([{
        "followers_count": float(followers),
        "friends_count": float(friends),
        "statuses_count": float(statuses),
        "favourites_count": float(favourites),
        "listed_count": float(listed),
        "default_profile_image": 1 if default_img else 0,
        "default_profile": 1 if default_profile else 0,
        "verified": 1 if verified else 0,
        "geo_enabled": 1 if geo else 0,
        "profile_use_background_image": 1 if header else 0,
        "protected": 1 if protected else 0,
        "lang": lang
    }])

    if st.button("🚀 Analyze Profile Authenticity", type="primary"):
        pred = model.predict(input_data)[0]
        probs = model.predict_proba(input_data)[0]
        fake_prob = probs[1]
        real_prob = probs[0]

        if pred == 1:
            st.error(f"⚠️ **FAKE / AUTOMATED BOT** ({fake_prob*100:.1f}% Probability)")
        else:
            st.success(f"✅ **AUTHENTIC REAL USER** ({real_prob*100:.1f}% Probability)")

        st.progress(float(fake_prob))
        st.write(f"**Bot Probability:** `{fake_prob*100:.2f}%` | **Real Probability:** `{real_prob*100:.2f}%`")

        ratio = followers / max(friends, 1)
        st.metric("Followers to Following Ratio", f"{ratio:.2f}")

        st.markdown("### 📌 Behavioral Insights")
        if default_img:
            st.warning("• Default avatar in use (often associated with disposable accounts).")
        if friends > 500 and ratio < 0.05:
            st.error("• Severe follower-following imbalance (high following, low followers).")
        if favourites == 0 and statuses > 20:
            st.warning("• Zero likes given despite active posting (typical of automated broadcasters).")
        if verified:
            st.info("• Account verified.")
