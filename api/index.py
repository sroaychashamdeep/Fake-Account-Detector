import sys
from pathlib import Path

# Add project root directory to sys.path so app and fake-account-detector can be imported
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Ensure fake-account-detector package is also accessible
PROJECT_DIR = ROOT_DIR / "fake-account-detector"
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from app import app
