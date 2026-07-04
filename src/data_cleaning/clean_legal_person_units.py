"""Build legal-person-unit panels from image-transcribed raw CSV files."""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path
from typing import Any


RAW_INDUSTRY_YEAR_CSV = Path(
    "data/raw/official_statistics/legal_person_units_industry_year_image_transcription.csv"
)
RAW_PROVINCE_INDUSTRY_CSV = Path(
    "data/raw/official_statistics/legal_person_units_province_industry_2024_image_transcription.csv"
)
OUTPUT_INDUSTRY_YEAR_CSV = Path("data/processed/legal_person_units_by_industry_year_panel.csv")
OUTPUT_PROVINCE_INDUSTRY_CSV = Path("data/processed/legal_person_units_by_province_industry_2024.csv")

UNIT = "个"
DATA_SCOPE_INDUSTRY_YEAR = "全国年度分行业"
DATA_SCOPE_PROVINCE_INDUSTRY = "2024年省级地区分行业"
SOURCE_TITLE = "《中国统计年鉴2025》"

INDUSTRIES = [
    ("total", "合计"),
    ("agriculture_forestry_animal_fishing", "农、林、牧、渔业"),
    ("mining", "采矿业"),
    ("manufacturing", "制造业"),
    ("electricity_heat_gas_water", "电力、热力、燃气及水生产和供应业"),
    ("construction", "建筑业"),
    ("wholesale_retail", "批发和零售业"),
    ("transport_storage_postal", "交通运输、仓储和邮政业"),
    ("accommodation_catering", "住宿和餐饮业"),
    ("information_software_it", "信息传输、软件和信息技术服务业"),
    ("finance", "金融业"),
    ("real_estate", "房地产业"),
    ("leasing_business_services", "租赁和商务服务业"),
    ("scientific_research_technical_services", "科学研究和技术服务业"),
    ("water_environment_public_facilities", "水利、环境和公共设施管理业"),
    ("resident_repair_other_services", "居民服务、修理和其他服务业"),
    ("education", "教育"),
    ("health_social_work", "卫生和社会工作"),
    ("culture_sports_entertainment", "文化、体育和娱乐业"),
    ("public_management_social_security_social_org", "公共管理、社会保障和社会组织"),
]

CSV_COLUMNS = [
    "year",
    "province",
    "industry_code",
    "industry_name",
    "legal_person_units",
    "total_units",
    "industry_share",
    "unit",
    "data_scope",
    "source",
    "source_file",
    "source_type",
    "confidence_flag",
    "note",
]


def build_industry_year_panel(input_csv: Path = RAW_INDUSTRY_YEAR_CSV) -> list[dict[str, Any]]:
    """Return national industry-year rows from the image-transcribed CSV."""

    rows: list[dict[str, Any]] = []
    for raw_row in _read_csv(input_csv):
        year = int(raw_row["year"])
        total_units = _to_number(raw_row["total"])
        for industry_code, industry_name in INDUSTRIES:
            value = _to_number(raw_row.get(industry_code, ""))
            rows.append(
                _build_row(
                    year=year,
                    province="全国",
                    industry_code=industry_code,
                    industry_name=industry_name,
                    legal_person_units=value,
                    total_units=total_units,
                    data_scope=DATA_SCOPE_INDUSTRY_YEAR,
                    source_file=input_csv,
                    raw_row=raw_row,
                )
            )
    return rows


def build_province_industry_panel(input_csv: Path = RAW_PROVINCE_INDUSTRY_CSV) -> list[dict[str, Any]]:
    """Return province-industry rows for 2024 from the image-transcribed CSV."""

    rows: list[dict[str, Any]] = []
    for raw_row in _read_csv(input_csv):
        year = int(raw_row["year"])
        province = raw_row["province"]
        total_units = _to_number(raw_row["total"])
        for industry_code, industry_name in INDUSTRIES:
            value = _to_number(raw_row.get(industry_code, ""))
            rows.append(
                _build_row(
                    year=year,
                    province=province,
                    industry_code=industry_code,
                    industry_name=industry_name,
                    legal_person_units=value,
                    total_units=total_units,
                    data_scope=DATA_SCOPE_PROVINCE_INDUSTRY,
                    source_file=input_csv,
                    raw_row=raw_row,
                )
            )
    return rows


def write_panel_csv(rows: list[dict[str, Any]], output_csv: Path) -> None:
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    with output_csv.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_csv_value(row.get(column)) for column in CSV_COLUMNS})


def _read_csv(input_csv: Path) -> list[dict[str, str]]:
    with input_csv.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))


def _build_row(
    *,
    year: int,
    province: str,
    industry_code: str,
    industry_name: str,
    legal_person_units: float,
    total_units: float,
    data_scope: str,
    source_file: Path,
    raw_row: dict[str, str],
) -> dict[str, Any]:
    return {
        "year": year,
        "province": province,
        "industry_code": industry_code,
        "industry_name": industry_name,
        "legal_person_units": legal_person_units,
        "total_units": total_units,
        "industry_share": _safe_divide(legal_person_units, total_units),
        "unit": UNIT,
        "data_scope": data_scope,
        "source": SOURCE_TITLE,
        "source_file": str(source_file).replace("\\", "/"),
        "source_type": raw_row.get("source_type", ""),
        "confidence_flag": raw_row.get("confidence_flag", ""),
        "note": raw_row.get("note", ""),
    }


def _to_number(value: Any) -> float:
    if value is None or str(value).strip() == "":
        return math.nan
    return float(str(value).replace(",", ""))


def _safe_divide(numerator: float, denominator: float) -> float:
    if _is_missing(numerator) or _is_missing(denominator) or denominator == 0:
        return math.nan
    return numerator / denominator


def _is_missing(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)


def _format_csv_value(value: Any) -> Any:
    if _is_missing(value):
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return value


def main() -> None:
    parser = argparse.ArgumentParser(description="Build legal person unit panels")
    parser.add_argument("--industry-year-input", type=Path, default=RAW_INDUSTRY_YEAR_CSV)
    parser.add_argument("--province-industry-input", type=Path, default=RAW_PROVINCE_INDUSTRY_CSV)
    parser.add_argument("--industry-year-output", type=Path, default=OUTPUT_INDUSTRY_YEAR_CSV)
    parser.add_argument("--province-industry-output", type=Path, default=OUTPUT_PROVINCE_INDUSTRY_CSV)
    args = parser.parse_args()

    industry_year_rows = build_industry_year_panel(args.industry_year_input)
    province_industry_rows = build_province_industry_panel(args.province_industry_input)
    write_panel_csv(industry_year_rows, args.industry_year_output)
    write_panel_csv(province_industry_rows, args.province_industry_output)
    print(f"Wrote {len(industry_year_rows)} rows to {args.industry_year_output}")
    print(f"Wrote {len(province_industry_rows)} rows to {args.province_industry_output}")


if __name__ == "__main__":
    main()
