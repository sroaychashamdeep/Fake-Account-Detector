"""Predict fake-account labels for a CSV or Excel file."""
from __future__ import annotations

import argparse
from pathlib import Path

import yaml

from src.models.predict_model import predict_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Add fake-account predictions to a new workbook.")
    parser.add_argument("input", type=Path, help="Input .csv, .xlsx, or .xls file")
    parser.add_argument("--output", type=Path, required=True, help="New .xlsx output path")
    parser.add_argument("--model", type=Path, help="Pipeline file; defaults to config.yaml")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent
    config = yaml.safe_load((root / "config.yaml").read_text(encoding="utf-8"))
    model_path = args.model or root / config["model"]["artifact"]
    result = predict_file(model_path, args.input, args.output)
    print(f"Wrote predictions for {len(result)} accounts to {args.output}")
    print("fake_probability is a model score, not a guarantee of authenticity.")


if __name__ == "__main__":
    main()
