"""Build a province-year panel for enterprise legal person units."""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data_cleaning.clean_graduate_supply import _format_csv_value, _read_first_sheet, _to_float


RAW_WORKBOOK = Path("data/raw/official_statistics/企业法人单位数_分省年度数据.xlsx")
OUTPUT_CSV = Path("data/processed/enterprise_units_by_province_panel.csv")

SOURCE_TITLE = "国家统计局：企业法人单位数_分省年度数据.xlsx"
DATA_SCOPE = "分省年度数据"
UNIT = "个"
NOTE = (
    "原表年份包括2016、2017、2019、2020、2021、2022、2024，缺少2018和2023；"
    "该指标为省级企业法人单位存量，不等同于招聘岗位数。"
)

CSV_COLUMNS = [
    "year",
    "province",
    "enterprise_legal_person_units",
    "unit",
    "data_scope",
    "source",
    "source_file",
    "note",
]


def build_enterprise_units_panel(workbook_path: Path = RAW_WORKBOOK) -> list[dict[str, Any]]:
    """Return one row per province and year from the enterprise units workbook."""

    table = _read_first_sheet(workbook_path)
    header_row_index = _find_header_row_index(table)
    header = table[header_row_index]
    years = [_parse_year(cell) for cell in header[1:]]

    rows: list[dict[str, Any]] = []
    for raw_row in table[header_row_index + 1 :]:
        if not raw_row:
            continue
        province = str(raw_row[0]).strip()
        if not province or province.startswith("数据来源"):
            break
        if province.startswith("注"):
            continue

        values = raw_row[1 : 1 + len(years)]
        for year, value in zip(years, values):
            if year is None:
                continue
            units = _to_float(value)
            if _is_missing(units):
                continue
            rows.append(
                {
                    "year": year,
                    "province": province,
                    "enterprise_legal_person_units": int(units),
                    "unit": UNIT,
                    "data_scope": DATA_SCOPE,
                    "source": SOURCE_TITLE,
                    "source_file": str(workbook_path).replace("\\", "/"),
                    "note": NOTE,
                }
            )

    return sorted(rows, key=lambda row: (row["year"], row["province"]))


def write_panel_csv(rows: list[dict[str, Any]], output_path: Path = OUTPUT_CSV) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_csv_value(row.get(column)) for column in CSV_COLUMNS})


def _find_header_row_index(table: list[list[Any]]) -> int:
    for index, row in enumerate(table):
        if row and str(row[0]).strip() == "地区":
            return index
    raise ValueError("Could not find region header row")


def _parse_year(value: Any) -> int | None:
    match = re.search(r"(\d{4})", str(value))
    return int(match.group(1)) if match else None


def _is_missing(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build enterprise_units_by_province_panel.csv")
    parser.add_argument("--input", type=Path, default=RAW_WORKBOOK)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = parser.parse_args()

    rows = build_enterprise_units_panel(args.input)
    write_panel_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
