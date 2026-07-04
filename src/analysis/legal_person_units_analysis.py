"""Analysis tables for legal-person-unit industry structure."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path
from typing import Any

import pandas as pd


INPUT_INDUSTRY_YEAR = Path("data/processed/legal_person_units_by_industry_year_panel.csv")
INPUT_RAW_INDUSTRY_YEAR = Path(
    "data/raw/official_statistics/legal_person_units_industry_year_image_transcription.csv"
)
INPUT_RAW_PROVINCE_INDUSTRY = Path(
    "data/raw/official_statistics/legal_person_units_province_industry_2024_image_transcription.csv"
)
OUTPUT_GROWTH_SUMMARY = Path("reports/tables/legal_person_units_industry_growth_summary.csv")
OUTPUT_QUALITY_CHECK = Path("reports/tables/legal_person_units_transcription_quality_check.csv")

NON_INDUSTRY_COLUMNS = {"year", "province", "source_type", "confidence_flag", "note"}


def build_industry_growth_summary(input_csv: Path = INPUT_INDUSTRY_YEAR) -> list[dict[str, Any]]:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    df = df[df["industry_code"] != "total"].copy()
    base = df[df["year"] == 2005][
        ["industry_code", "industry_name", "legal_person_units", "industry_share"]
    ].rename(columns={"legal_person_units": "units_2005", "industry_share": "share_2005"})
    final = df[df["year"] == 2024][
        ["industry_code", "legal_person_units", "industry_share"]
    ].rename(columns={"legal_person_units": "units_2024", "industry_share": "share_2024"})
    merged = base.merge(final, on="industry_code", how="inner")
    merged["growth_multiple_2005_2024"] = merged["units_2024"] / merged["units_2005"]
    merged["share_change_2005_2024"] = merged["share_2024"] - merged["share_2005"]
    merged = merged.sort_values("growth_multiple_2005_2024", ascending=False)
    return merged.to_dict("records")


def build_transcription_quality_check(
    raw_industry_year_csv: Path = INPUT_RAW_INDUSTRY_YEAR,
    raw_province_industry_csv: Path = INPUT_RAW_PROVINCE_INDUSTRY,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    rows.extend(_quality_rows(raw_industry_year_csv, "全国年度", key_column="year"))
    rows.extend(_quality_rows(raw_province_industry_csv, "2024省级地区", key_column="province"))
    return rows


def write_csv(rows: list[dict[str, Any]], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _quality_rows(input_csv: Path, scope: str, key_column: str) -> list[dict[str, Any]]:
    df = pd.read_csv(input_csv, encoding="utf-8-sig")
    industry_columns = [
        column
        for column in df.columns
        if column not in NON_INDUSTRY_COLUMNS and column not in {"total"}
    ]
    result: list[dict[str, Any]] = []
    for _, row in df.iterrows():
        total = float(row["total"])
        industry_sum = float(row[industry_columns].sum(skipna=True))
        gap = total - industry_sum
        row_key = f"全国-{int(row['year'])}" if key_column == "year" else f"{row[key_column]}-{int(row['year'])}"
        result.append(
            {
                "scope": scope,
                "row_key": row_key,
                "total": int(total),
                "sum_industries": int(industry_sum),
                "gap": int(gap),
                "requires_review": abs(gap) > 0,
                "source_file": str(input_csv).replace("\\", "/"),
                "note": row.get("note", ""),
            }
        )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Build legal person unit analysis tables")
    parser.add_argument("--industry-year-input", type=Path, default=INPUT_INDUSTRY_YEAR)
    parser.add_argument("--raw-industry-year-input", type=Path, default=INPUT_RAW_INDUSTRY_YEAR)
    parser.add_argument("--raw-province-industry-input", type=Path, default=INPUT_RAW_PROVINCE_INDUSTRY)
    parser.add_argument("--growth-output", type=Path, default=OUTPUT_GROWTH_SUMMARY)
    parser.add_argument("--quality-output", type=Path, default=OUTPUT_QUALITY_CHECK)
    args = parser.parse_args()

    growth_rows = build_industry_growth_summary(args.industry_year_input)
    quality_rows = build_transcription_quality_check(
        args.raw_industry_year_input,
        args.raw_province_industry_input,
    )
    write_csv(growth_rows, args.growth_output)
    write_csv(quality_rows, args.quality_output)
    print(f"Wrote {len(growth_rows)} rows to {args.growth_output}")
    print(f"Wrote {len(quality_rows)} rows to {args.quality_output}")


if __name__ == "__main__":
    main()
