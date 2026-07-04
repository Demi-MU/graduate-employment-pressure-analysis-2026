"""Build an age-group panel from the population sample workbook."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.data_cleaning.clean_graduate_supply import _format_csv_value, _read_first_sheet, _to_float


RAW_WORKBOOK = Path("data/raw/official_statistics/人口抽样调查样本数据_年度数据.xlsx")
OUTPUT_CSV = Path("data/processed/population_sample_age_panel.csv")

SOURCE_TITLE = "人口抽样调查样本数据_年度数据.xlsx"
DATA_SCOPE = "人口抽样调查样本数据"
UNIT = "人"
NOTE = (
    "该数据为人口抽样调查样本数据，适合观察年龄结构占比变化，"
    "不代表全国实际人口规模。"
)

CSV_COLUMNS = [
    "year",
    "age_group",
    "population_sample_count",
    "total_sample_count",
    "age_group_share",
    "unit",
    "data_scope",
    "source",
    "source_file",
    "note",
]


def build_population_sample_age_panel(workbook_path: Path = RAW_WORKBOOK) -> list[dict[str, Any]]:
    """Return one row per year and age group from the population sample workbook."""

    table = _read_first_sheet(workbook_path)
    header_row_index = _find_header_row_index(table)
    header = table[header_row_index]
    years = [_parse_year(cell) for cell in header[1:]]

    age_rows: dict[str, list[float]] = {}
    total_counts: list[float] | None = None
    for row in table[header_row_index + 1 :]:
        if not row:
            continue
        label = str(row[0]).strip()
        if label.startswith("注：") or label.startswith("数据来源"):
            break
        values = [_to_float(cell) for cell in row[1 : 1 + len(years)]]
        if label.startswith("人口数 "):
            total_counts = values
            continue
        age_group = _extract_age_group(label)
        if age_group:
            age_rows[age_group] = values

    if total_counts is None:
        raise ValueError("Could not find total sample count row")

    age_rows["20-29岁"] = _sum_series(age_rows["20-24岁"], age_rows["25-29岁"])
    age_rows["15-29岁"] = _sum_series(age_rows["15-19岁"], age_rows["20-24岁"], age_rows["25-29岁"])

    rows: list[dict[str, Any]] = []
    for index, year in enumerate(years):
        if year is None:
            continue
        total_count = total_counts[index]
        for age_group, values in age_rows.items():
            sample_count = values[index]
            rows.append(
                {
                    "year": year,
                    "age_group": age_group,
                    "population_sample_count": sample_count,
                    "total_sample_count": total_count,
                    "age_group_share": sample_count / total_count if total_count else float("nan"),
                    "unit": UNIT,
                    "data_scope": DATA_SCOPE,
                    "source": SOURCE_TITLE,
                    "source_file": str(workbook_path).replace("\\", "/"),
                    "note": NOTE,
                }
            )
    return sorted(rows, key=lambda row: (row["year"], _age_sort_key(row["age_group"])))


def write_panel_csv(rows: list[dict[str, Any]], output_path: Path = OUTPUT_CSV) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_csv_value(row.get(column)) for column in CSV_COLUMNS})


def _find_header_row_index(table: list[list[Any]]) -> int:
    for index, row in enumerate(table):
        if row and str(row[0]).strip() == "指标":
            return index
    raise ValueError("Could not find indicator header row")


def _parse_year(value: Any) -> int | None:
    match = re.search(r"(\d{4})", str(value))
    return int(match.group(1)) if match else None


def _extract_age_group(label: str) -> str | None:
    match = re.match(r"(.+?)人口数\s*\(人口抽样调查\)", label)
    return match.group(1).strip() if match else None


def _sum_series(*series: list[float]) -> list[float]:
    return [sum(values) for values in zip(*series)]


def _age_sort_key(age_group: str) -> tuple[int, int]:
    if age_group == "20-29岁":
        return (20, 29)
    if age_group == "15-29岁":
        return (15, 29)
    if age_group == "95岁以上":
        return (95, 999)
    match = re.match(r"(\d+)-(\d+)岁", age_group)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (999, 999)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build population_sample_age_panel.csv")
    parser.add_argument("--input", type=Path, default=RAW_WORKBOOK)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = parser.parse_args()

    rows = build_population_sample_age_panel(args.input)
    write_panel_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
