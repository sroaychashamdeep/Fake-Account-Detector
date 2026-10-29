# VeriProfile AI - Social Media Fake Account Detector

An end-to-end Machine Learning web application and API that detects whether a social media account is an authentic user or an automated fake/bot profile. Features an interactive web dashboard, batch Excel/CSV scanning, and live Instagram profile scraping powered by the **Apify Instagram Profile Scraper**.

---

## 🌟 Key Features

* **Interactive Web Dashboard**: Built with FastAPI and Tailwind CSS for instant diagnosis.
* **Live Instagram Verification**: Scrapes real-time Instagram account metrics via Apify Cloud (`apify/instagram-profile-scraper`) and runs them through the ML pipeline.
* **Pre-trained ML Model**: High-performing Random Forest Classifier achieving **97.7% test accuracy** and **96.5% validation F1 score**.
* **Behavioral Diagnostics**: Evaluates follower-to-following ratios, avatar customization, zero-engagement broadcasting, and posting history.
* **Spreadsheet Batch Scanner**: Upload `.xlsx` or `.csv` files to audit hundreds of accounts simultaneously.
* **REST API**: Automated endpoints (`/api/predict`, `/api/scan-instagram`, `/api/batch-predict`) with full OpenAPI documentation at `/docs`.

---

## 🏗️ Architecture & Pipeline

* **Data Sources**: Audited datasets of authentic vs fake profiles (~4,000 training accounts, 1,002 test accounts).
* **Feature Pipeline**:
  * Quantitative counts: `followers_count`, `friends_count`, `statuses_count`, `favourites_count`, `listed_count`.
  * Profile flags: `default_profile_image`, `default_profile`, `verified`, `geo_enabled`, `protected`, `profile_use_background_image`.
  * Median numerical imputation with missingness indicators + standard scaling.
  * One-hot encoding for categorical attributes.
* **Model**: `RandomForestClassifier` with balanced class weights (400 estimators).

---

## 🚀 Quick Start

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/sroaychashamdeep/<repo-name>.git
cd <repo-name>
pip install -r fake-account-detector/requirements.txt
pip install fastapi uvicorn python-dotenv apify-client
```

### 2. Configure Environment (Optional for Live Instagram Scraping)
Create a `.env` file in the root directory:
```env
APIFY_TOKEN=your_apify_api_token_here
```

### 3. Run the Web Server
Launch the application:
```bash
python app.py
```
Or double-click `start_server.bat` on Windows.

Open your browser at **http://localhost:8000**.

---

## 📸 Usage

* **Single Profile Inspector**: Input profile statistics or use one-click autofill presets (Spam Bot, Real User, Public Figure, Lurker).
* **Live Instagram Tab**: Type an Instagram handle (e.g. `@username`) to fetch and inspect the profile live.
* **Batch Scanner**: Drag and drop an Excel or CSV file to view full classification results and download predictions.

---

## 📄 License
MIT License
