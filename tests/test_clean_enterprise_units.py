import unittest
from pathlib import Path

from src.data_cleaning.clean_enterprise_units import build_enterprise_units_panel


class EnterpriseUnitsPanelTest(unittest.TestCase):
    def test_builds_province_year_panel_from_raw_workbook(self):
        rows = build_enterprise_units_panel(
            Path("data/raw/official_statistics/企业法人单位数_分省年度数据.xlsx")
        )

        self.assertEqual(len(rows), 217)
        self.assertEqual(min(row["year"] for row in rows), 2016)
        self.assertEqual(max(row["year"] for row in rows), 2024)

        guangdong_2024 = next(
            row for row in rows if row["province"] == "广东省" and row["year"] == 2024
        )
        self.assertEqual(guangdong_2024["enterprise_legal_person_units"], 4640153)
        self.assertEqual(guangdong_2024["unit"], "个")
        self.assertIn("国家统计局", guangdong_2024["source"])

        beijing_2016 = next(
            row for row in rows if row["province"] == "北京市" and row["year"] == 2016
        )
        self.assertEqual(beijing_2016["enterprise_legal_person_units"], 669663)
        self.assertIn("2018", beijing_2016["note"])
        self.assertIn("2023", beijing_2016["note"])


if __name__ == "__main__":
    unittest.main()
