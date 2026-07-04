import math
import unittest
from pathlib import Path

from src.data_cleaning.clean_legal_person_units import (
    build_industry_year_panel,
    build_province_industry_panel,
)


class LegalPersonUnitsPanelTest(unittest.TestCase):
    def test_builds_industry_year_long_panel(self):
        rows = build_industry_year_panel(
            Path("data/raw/official_statistics/legal_person_units_industry_year_image_transcription.csv")
        )

        self.assertEqual(len(rows), 400)

        information_2024 = next(
            row
            for row in rows
            if row["year"] == 2024 and row["industry_code"] == "information_software_it"
        )
        self.assertEqual(information_2024["legal_person_units"], 1896012)
        self.assertAlmostEqual(information_2024["industry_share"], 1896012 / 37782288)
        self.assertEqual(information_2024["confidence_flag"], "needs_review")

        finance_2013 = next(
            row for row in rows if row["year"] == 2013 and row["industry_code"] == "finance"
        )
        self.assertTrue(math.isnan(finance_2013["legal_person_units"]))
        self.assertTrue(math.isnan(finance_2013["industry_share"]))
        self.assertIn("2013", finance_2013["note"])

    def test_builds_province_industry_2024_long_panel(self):
        rows = build_province_industry_panel(
            Path(
                "data/raw/official_statistics/"
                "legal_person_units_province_industry_2024_image_transcription.csv"
            )
        )

        self.assertEqual(len(rows), 620)

        guangdong_wholesale = next(
            row
            for row in rows
            if row["province"] == "广东省" and row["industry_code"] == "wholesale_retail"
        )
        self.assertEqual(guangdong_wholesale["legal_person_units"], 1617646)
        self.assertAlmostEqual(guangdong_wholesale["industry_share"], 1617646 / 4989249)

        beijing_science = next(
            row
            for row in rows
            if row["province"] == "北京市"
            and row["industry_code"] == "scientific_research_technical_services"
        )
        self.assertEqual(beijing_science["legal_person_units"], 226230)
        self.assertEqual(beijing_science["source_type"], "image_transcription")


if __name__ == "__main__":
    unittest.main()
