"""Clean screenshot-transcribed Liepin university job demand data."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


INPUT_CSV = Path("data/raw/recruitment_reports/liepin_university_job_demand_image_transcription.csv")
OUTPUT_CSV = Path("data/processed/liepin_university_job_demand_structure.csv")

GROUP_LABELS = {
    "education_requirement": "岗位学历要求",
    "registered_capital": "企业注册资本",
    "company_type": "企业性质",
}

EXPECTED_GROUP_COUNTS = {
    "education_requirement": 12,
    "registered_capital": 12,
    "company_type": 16,
}


def clean_liepin_university_job_demand(
    input_csv: Path = INPUT_CSV,
    output_path: Path | None = OUTPUT_CSV,
) -> pd.DataFrame:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    required_columns = {
        "indicator_group",
        "category_order",
        "category",
        "period",
        "period_label",
        "percentage",
        "source",
        "source_type",
        "confidence_flag",
        "note",
    }
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    cleaned = df.copy()
    cleaned["indicator_group"] = cleaned["indicator_group"].str.strip()
    cleaned["indicator_group_name"] = cleaned["indicator_group"].map(GROUP_LABELS)
    if cleaned["indicator_group_name"].isna().any():
        unknown = sorted(cleaned.loc[cleaned["indicator_group_name"].isna(), "indicator_group"].unique())
        raise ValueError(f"Unknown indicator_group values: {unknown}")

    cleaned["category_order"] = cleaned["category_order"].astype(int)
    cleaned["percentage"] = pd.to_numeric(cleaned["percentage"], errors="raise").astype(float)
    cleaned["unit"] = "percent"

    group_counts = cleaned.groupby("indicator_group").size().to_dict()
    if group_counts != EXPECTED_GROUP_COUNTS:
        raise ValueError(f"Unexpected group counts: {group_counts}")

    duplicate_mask = cleaned.duplicated(["indicator_group", "category", "period"], keep=False)
    if duplicate_mask.any():
        duplicates = cleaned.loc[duplicate_mask, ["indicator_group", "category", "period"]]
        raise ValueError(f"Duplicate category-period rows: {duplicates.to_dict('records')}")

    cleaned = cleaned[
        [   "indicator_group",
            "indicator_group_name",
            "category_order",
            "category",
            "period",
            "period_label",
            "percentage",
            "unit",
            "source",
            "source_type",
            "confidence_flag",
            "note",
        ]
    ].sort_values([ "indicator_group","category_order", "period"])

    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        cleaned.to_csv(output_path, index=False, encoding="utf-8-sig")

    return cleaned.reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean Liepin university job demand screenshot data")
    parser.add_argument("--input", type=Path, default=INPUT_CSV)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = parser.parse_args()

    cleaned = clean_liepin_university_job_demand(args.input, args.output)
    print(f"Wrote {args.output} ({len(cleaned)} rows)")


if __name__ == "__main__":
    main()
