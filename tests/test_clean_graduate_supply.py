import math
import unittest
from pathlib import Path

from src.data_cleaning.clean_graduate_supply import build_graduate_supply_panel


class GraduateSupplyPanelTest(unittest.TestCase):
    def test_builds_core_supply_panel_from_raw_workbook(self):
        workbook_path = Path("data/raw/official_statistics/教育-年度数据.xlsx")

        rows = build_graduate_supply_panel(workbook_path)

        self.assertEqual(rows[0]["year"], 2011)
        self.assertEqual(rows[-1]["year"], 2025)
        self.assertEqual(len(rows), 15)

        row_2025 = next(row for row in rows if row["year"] == 2025)
        self.assertAlmostEqual(row_2025["postgraduate_graduates"], 116.7)
        self.assertAlmostEqual(row_2025["undergraduate_vocational_graduates"], 1105.1)
        self.assertAlmostEqual(row_2025["graduate_total"], 1221.8)
        self.assertAlmostEqual(
            row_2025["postgraduate_share"],
            116.7 / 1221.8,
        )
        self.assertTrue(math.isnan(row_2025["master_graduates"]))
        self.assertTrue(math.isnan(row_2025["doctoral_graduates"]))

        row_2024 = next(row for row in rows if row["year"] == 2024)
        self.assertAlmostEqual(row_2024["master_graduates"], 98.641)
        self.assertAlmostEqual(row_2024["doctoral_graduates"], 9.7185)
        self.assertAlmostEqual(row_2024["graduate_total"], 1167.7595)


if __name__ == "__main__":
    unittest.main()
