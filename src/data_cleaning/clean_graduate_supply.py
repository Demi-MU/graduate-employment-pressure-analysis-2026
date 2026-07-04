"""Build the graduate supply panel from the raw education annual workbook."""

from __future__ import annotations

import argparse
import csv
import math
import re
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


RAW_WORKBOOK = Path("data/raw/official_statistics/教育-年度数据.xlsx")
OUTPUT_CSV = Path("data/processed/graduate_supply_panel.csv")

COUNT_UNIT = "万人"
SOURCE_TITLE = "教育-年度数据.xlsx"
DATA_SCOPE = "年度统计口径"

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
RELS_NS = {"pr": "http://schemas.openxmlformats.org/package/2006/relationships"}

TARGET_INDICATORS = {
    "postgraduate_graduates": "研究生毕 (结) 业生数 (万人)",
    "master_graduates": "硕士毕 (结) 业生数 (万人)",
    "doctoral_graduates": "博士毕 (结) 业生数 (万人)",
    "undergraduate_vocational_graduates": "普通本科、专科生毕 (结) 业生数 (万人)",
    "undergraduate_graduates": "普通本科毕 (结) 业生数 (万人)",
    "vocational_graduates": "普通专科毕 (结) 业生数 (万人)",
}

CSV_COLUMNS = [
    "year",
    "graduate_total",
    "undergraduate_vocational_graduates",
    "undergraduate_graduates",
    "vocational_graduates",
    "postgraduate_graduates",
    "master_graduates",
    "doctoral_graduates",
    "postgraduate_share",
    "master_share",
    "unit",
    "data_scope",
    "source",
    "source_file",
    "note",
]


def build_graduate_supply_panel(workbook_path: Path = RAW_WORKBOOK) -> list[dict[str, Any]]:
    """Read the annual education workbook and return one row per year."""

    table = _read_first_sheet(workbook_path)
    if not table:
        raise ValueError(f"No worksheet data found in {workbook_path}")

    header = table[0]
    years = [_parse_year(cell) for cell in header[1:]]
    indicator_rows = {_normalize(row[0]): row[1:] for row in table[1:] if row}

    rows: list[dict[str, Any]] = []
    for index, year in enumerate(years):
        if year is None:
            continue

        row: dict[str, Any] = {"year": year}
        for output_name, source_label in TARGET_INDICATORS.items():
            values = indicator_rows.get(_normalize(source_label))
            row[output_name] = _to_float(values[index]) if values and index < len(values) else math.nan

        row["graduate_total"] = _sum_skip_nan(
            row["undergraduate_vocational_graduates"],
            row["postgraduate_graduates"],
        )
        row["postgraduate_share"] = _safe_divide(
            row["postgraduate_graduates"],
            row["graduate_total"],
        )
        row["master_share"] = _safe_divide(row["master_graduates"], row["graduate_total"])
        row["unit"] = COUNT_UNIT
        row["data_scope"] = DATA_SCOPE
        row["source"] = SOURCE_TITLE
        row["source_file"] = str(workbook_path).replace("\\", "/")
        row["note"] = _note_for_row(row)
        rows.append(row)

    return sorted(rows, key=lambda item: item["year"])


def write_panel_csv(rows: list[dict[str, Any]], output_path: Path = OUTPUT_CSV) -> None:
    """Write the panel to CSV with blanks for missing numeric values."""

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: _format_csv_value(row.get(column)) for column in CSV_COLUMNS})


def _read_first_sheet(workbook_path: Path) -> list[list[Any]]:
    if not workbook_path.exists():
        raise FileNotFoundError(workbook_path)

    with zipfile.ZipFile(workbook_path) as archive:
        shared_strings = _read_shared_strings(archive)
        sheet_path = _first_sheet_path(archive)
        root = ET.fromstring(archive.read(sheet_path))

    table: list[list[Any]] = []
    for row in root.findall("a:sheetData/a:row", NS):
        values: dict[int, Any] = {}
        for cell in row.findall("a:c", NS):
            reference = cell.attrib.get("r", "")
            match = re.match(r"([A-Z]+)(\d+)", reference)
            if not match:
                continue
            column_index = _column_to_index(match.group(1))
            values[column_index] = _cell_value(cell, shared_strings)
        if values:
            table.append([values.get(index, "") for index in range(1, max(values) + 1)])
    return table


def _read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join(text.text or "" for text in item.findall(".//a:t", NS)) for item in root.findall("a:si", NS)]


def _first_sheet_path(archive: zipfile.ZipFile) -> str:
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    relationship_map = {
        relationship.attrib["Id"]: relationship.attrib["Target"]
        for relationship in relationships.findall("pr:Relationship", RELS_NS)
    }
    first_sheet = workbook.find("a:sheets/a:sheet", NS)
    if first_sheet is None:
        raise ValueError("Workbook contains no sheets")

    relationship_id = first_sheet.attrib[
        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
    ]
    target = relationship_map[relationship_id]
    if target.startswith("/"):
        return target.lstrip("/")
    if target.startswith("xl/"):
        return target
    return f"xl/{target}"


def _cell_value(cell: ET.Element, shared_strings: list[str]) -> Any:
    cell_type = cell.attrib.get("t")
    if cell_type == "s":
        value = cell.find("a:v", NS)
        return shared_strings[int(value.text)] if value is not None and value.text is not None else ""
    if cell_type == "inlineStr":
        return "".join(text.text or "" for text in cell.findall(".//a:t", NS))

    value = cell.find("a:v", NS)
    if value is None or value.text is None:
        return ""
    return _to_float(value.text)


def _column_to_index(column: str) -> int:
    result = 0
    for char in column:
        result = result * 26 + ord(char) - ord("A") + 1
    return result


def _parse_year(value: Any) -> int | None:
    match = re.search(r"(\d{4})", str(value))
    return int(match.group(1)) if match else None


def _normalize(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value)).strip()


def _to_float(value: Any) -> float:
    if value == "" or value is None:
        return math.nan
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def _is_missing(value: Any) -> bool:
    return isinstance(value, float) and math.isnan(value)


def _sum_skip_nan(*values: float) -> float:
    valid_values = [value for value in values if not _is_missing(value)]
    return sum(valid_values) if valid_values else math.nan


def _safe_divide(numerator: float, denominator: float) -> float:
    if _is_missing(numerator) or _is_missing(denominator) or denominator == 0:
        return math.nan
    return numerator / denominator


def _format_csv_value(value: Any) -> Any:
    if _is_missing(value):
        return ""
    if isinstance(value, float):
        return f"{value:.10g}"
    return value


def _note_for_row(row: dict[str, Any]) -> str:
    notes = [
        "graduate_total=普通本科、专科生毕(结)业生数+研究生毕(结)业生数",
    ]
    if _is_missing(row.get("master_graduates")) or _is_missing(row.get("doctoral_graduates")):
        notes.append("硕士/博士分项原表缺失")
    return "；".join(notes)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build graduate_supply_panel.csv")
    parser.add_argument("--input", type=Path, default=RAW_WORKBOOK)
    parser.add_argument("--output", type=Path, default=OUTPUT_CSV)
    args = parser.parse_args()

    rows = build_graduate_supply_panel(args.input)
    write_panel_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")


if __name__ == "__main__":
    main()
