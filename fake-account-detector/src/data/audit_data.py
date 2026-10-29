"""Create a complete, read-only audit report for the approved source workbooks."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.load_data import TARGET, load_workbook


IDENTIFIER_COLUMNS = ["id", "screen_name", "name", "url", "profile_image_url", "profile_image_url_https"]
SOURCE_COLUMNS = ["dataset", "RAND", "random_order"]
COUNT_COLUMNS = ["statuses_count", "followers_count", "friends_count", "favourites_count", "listed_count"]
BOOLEAN_COLUMNS = [
    "default_profile", "default_profile_image", "geo_enabled",
    "profile_use_background_image", "profile_background_tile", "protected", "verified",
]


def _duplicate_keys(frame: pd.DataFrame, column: str) -> dict[str, int]:
    if column not in frame:
        return {"unique_nonmissing": 0, "duplicate_nonmissing": 0, "zero_placeholders": 0}
    series = frame[column].dropna()
    zero = int(series.astype(str).str.strip().isin(["0", "0.0"]).sum()) if column == "id" else 0
    values = series.astype(str).str.strip().str.casefold()
    values = values[~values.isin(["", "0", "0.0"])]
    return {"unique_nonmissing": int(values.nunique()), "duplicate_nonmissing": int(values.duplicated().sum()), "zero_placeholders": zero}


def _workbook_summary(path: Path) -> dict[str, Any]:
    frame = load_workbook(path)
    details: dict[str, Any] = {
        "file": path.name, "rows": int(len(frame)), "columns": int(len(frame.columns)),
        "column_details": {}, "exact_duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_identifiers": {}, "label_distribution": {}, "numeric_checks": {},
        "all_numeric_checks": {},
    }
    for column in frame.columns:
        details["column_details"][str(column)] = {
            "dtype": str(frame[column].dtype),
            "missing": int(frame[column].isna().sum()),
            "nonmissing_unique": int(frame[column].nunique(dropna=True)),
        }
    for column in IDENTIFIER_COLUMNS:
        if column in frame:
            details["duplicate_identifiers"][column] = _duplicate_keys(frame, column)
    if TARGET in frame:
        details["label_distribution"] = {
            str(key): int(value) for key, value in frame[TARGET].value_counts(dropna=False).items()
        }
    for column in COUNT_COLUMNS:
        if column not in frame:
            continue
        values = pd.to_numeric(frame[column], errors="coerce").dropna()
        details["numeric_checks"][column] = {
            "min": float(values.min()) if len(values) else None,
            "max": float(values.max()) if len(values) else None,
            "negative_values": int((values < 0).sum()),
            "fractional_values": int((~np.isclose(values, np.round(values))).sum()),
        }
    for column in frame.select_dtypes(include="number").columns:
        values = pd.to_numeric(frame[column], errors="coerce")
        finite = values[np.isfinite(values)]
        item: dict[str, Any] = {
            "min": float(finite.min()) if len(finite) else None,
            "max": float(finite.max()) if len(finite) else None,
            "non_finite_values": int((values.notna() & ~np.isfinite(values)).sum()),
        }
        if column in BOOLEAN_COLUMNS:
            item["outside_0_1"] = int(((finite < 0) | (finite > 1)).sum())
            item["fractional_values"] = int((~np.isclose(finite, np.round(finite))).sum())
        details["all_numeric_checks"][str(column)] = item
    details["available_leakage_columns"] = [c for c in IDENTIFIER_COLUMNS + SOURCE_COLUMNS if c in frame]
    if "dataset" in frame and TARGET in frame:
        details["dataset_by_label"] = {
            str(k): {str(label): int(count) for label, count in val.items()}
            for k, val in pd.crosstab(frame["dataset"].fillna("<missing>"), frame[TARGET]).to_dict(orient="index").items()
        }
    return details


def _normalized_values(frame: pd.DataFrame, column: str) -> set[str]:
    if column not in frame:
        return set()
    values = set(frame[column].dropna().astype(str).str.strip().str.casefold())
    return values - {"", "0", "0.0"}


def audit_files(paths: dict[str, Path], report_path: Path) -> dict[str, Any]:
    """Audit workbook metadata, labels, values, schemas, duplicates, and overlap."""
    frames = {key: load_workbook(path) for key, path in paths.items()}
    summaries = {key: _workbook_summary(path) for key, path in paths.items()}
    fake_cols, real_cols, test_cols = (set(frames[k].columns) for k in ("fake", "real", "test"))
    train = pd.concat([frames["fake"], frames["real"]], ignore_index=True)
    schema = {
        "training_match": fake_cols == real_cols,
        "fake_only_columns": sorted(fake_cols - real_cols),
        "real_only_columns": sorted(real_cols - fake_cols),
        "test_only_columns_vs_training": sorted(test_cols - (fake_cols & real_cols)),
        "training_only_columns_vs_test": sorted((fake_cols & real_cols) - test_cols),
        "training_dtype_mismatches": {
            c: {"fake": str(frames["fake"][c].dtype), "real": str(frames["real"][c].dtype)}
            for c in sorted(fake_cols & real_cols)
            if frames["fake"][c].dtype != frames["real"][c].dtype
        },
        "test_dtype_mismatches": {
            c: {"training_fake": str(frames["fake"][c].dtype), "test": str(frames["test"][c].dtype)}
            for c in sorted(fake_cols & test_cols)
            if frames["fake"][c].dtype != frames["test"][c].dtype
        },
    }
    overlap: dict[str, Any] = {"exact_records": 0, "fake_real_account_overlap": {}, "identifier_fields": {}}
    for col in ["id", "screen_name", "profile_image_url_https", "profile_image_url", "name"]:
        fake_values = _normalized_values(frames["fake"], col)
        real_values = _normalized_values(frames["real"], col)
        if col in frames["fake"] and col in frames["real"]:
            overlap["fake_real_account_overlap"][col] = {
                "unique_fake": len(fake_values), "unique_real": len(real_values),
                "unique_overlap": len(fake_values & real_values),
            }
    common = [c for c in train if c in frames["test"] and c != "RAND"]
    def keys(frame: pd.DataFrame) -> set[tuple[str, ...]]:
        return set(map(tuple, frame[common].astype("string").fillna("<NA>").to_numpy().tolist()))
    overlap["exact_records"] = len(keys(train) & keys(frames["test"]))
    for col in ["id", "screen_name", "profile_image_url_https", "profile_image_url", "name", "url"]:
        train_values, test_values = _normalized_values(train, col), _normalized_values(frames["test"], col)
        if col in train and col in frames["test"]:
            overlap["identifier_fields"][col] = {
                "unique_train": len(train_values), "unique_test": len(test_values),
                "unique_overlap": len(train_values & test_values),
                "test_rows_matching_train": int(frames["test"][col].astype("string").str.strip().str.casefold().isin(train_values).sum()),
            }
    dataset_label = {}
    for name, frame in frames.items():
        if "dataset" in frame and TARGET in frame:
            dataset_label[name] = pd.crosstab(frame["dataset"].fillna("<missing>"), frame[TARGET]).to_dict(orient="index")
    report: dict[str, Any] = {
        "workbooks": summaries, "schema_comparison": schema,
        "train_test_overlap": overlap, "dataset_label_relationship": dataset_label,
        "findings": [
            "The requested merged testing(1).xlsx filename is absent; merged testing.xlsx is the only provided test workbook and is the one audited.",
            "The two training sources have no shared non-placeholder IDs or screen names; one profile image URL value is shared across each image URL field, which may be a common/default asset rather than the same account.",
            "The updated snapshot timestamp has one observed unique value per training source and is therefore excluded, along with created_at, to avoid deriving source-specific account-age features.",
            "Training dataset values are class-associated and must not be model features.",
            "The test workbook contains a RAND field; exclude it as a row-order/randomization artifact.",
            "Account identifiers, profile names, handles, URLs, and image URLs are excluded from model features.",
            "Test records overlap training records/accounts; test scores are not an independent generalization estimate.",
        ],
    }
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(_render_report(report), encoding="utf-8")
    report_path.with_suffix(".json").write_text(json.dumps(report, indent=2, default=str), encoding="utf-8")
    return report


def _render_report(report: dict[str, Any]) -> str:
    lines = ["# Data audit report", "", "Read-only audit of the three supplied source workbooks. Original files were not modified.", ""]
    for name, book in report["workbooks"].items():
        lines += [f"## {name}: `{Path(book['file']).name}`", "", f"- Rows: {book['rows']}", f"- Columns: {book['columns']}", f"- Exact duplicate rows: {book['exact_duplicate_rows']}", f"- Label distribution: `{book['label_distribution']}`", f"- Potential identifier columns found: `{book['available_leakage_columns']}`", "", "### Column types and missing values", "", "| Column | Type | Missing | Unique non-missing |", "|---|---:|---:|---:|"]
        for column, detail in book["column_details"].items():
            lines.append(f"| `{column}` | {detail['dtype']} | {detail['missing']} | {detail['nonmissing_unique']} |")
        lines += ["", "### Duplicate identifier diagnostics", "", "| Column | Unique non-missing | Duplicate non-missing | Zero placeholders |", "|---|---:|---:|---:|"]
        for column, detail in book["duplicate_identifiers"].items():
            lines.append(f"| `{column}` | {detail['unique_nonmissing']} | {detail['duplicate_nonmissing']} | {detail['zero_placeholders']} |")
        lines += ["", "### Count-field plausibility checks", "", "| Column | Min | Max | Negative | Fractional |", "|---|---:|---:|---:|---:|"]
        for column, detail in book["numeric_checks"].items():
            lines.append(f"| `{column}` | {detail['min']} | {detail['max']} | {detail['negative_values']} | {detail['fractional_values']} |")
        lines += ["", "### Other numeric-field checks", "", "| Column | Min | Max | Non-finite | Outside 0-1 (boolean-like) | Fractional (boolean-like) |", "|---|---:|---:|---:|---:|---:|"]
        for column, detail in book["all_numeric_checks"].items():
            lines.append(f"| `{column}` | {detail['min']} | {detail['max']} | {detail['non_finite_values']} | {detail.get('outside_0_1', 'n/a')} | {detail.get('fractional_values', 'n/a')} |")
        lines += [""]
        if book.get("dataset_by_label"):
            lines += ["Dataset-source values by label:", "", "```json", json.dumps(book["dataset_by_label"], indent=2), "```", ""]
    lines += ["## Schema comparison", "", "```json", json.dumps(report["schema_comparison"], indent=2), "```", "", "## Training/test overlap", "", "```json", json.dumps(report["train_test_overlap"], indent=2), "```", "", "## Leakage and interpretation findings", ""]
    lines += [f"- {item}" for item in report["findings"]]
    lines += ["", "## Limitations", "", "Count fields contain fractional and zero-placeholder values, and many IDs are repeated or zero. These values are reported as supplied; no source value was silently repaired. `dataset` is a direct source proxy for the target, and `RAND` is excluded. Exact shared records and account-identifier overlap mean the requested test evaluation is contaminated by overlap and is reported with that limitation.", ""]
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    audit_files({
        "fake": root / "data/raw/fake_users training.xlsx",
        "real": root / "data/raw/real_users training.xlsx",
        "test": root / "data/raw/merged testing.xlsx",
    }, root / "reports/data_audit.md")
    print(f"Wrote {root / 'reports/data_audit.md'}")


if __name__ == "__main__":
    main()
