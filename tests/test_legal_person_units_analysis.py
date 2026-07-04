import unittest
from pathlib import Path

from src.analysis.legal_person_units_analysis import (
    build_industry_growth_summary,
    build_transcription_quality_check,
)


class LegalPersonUnitsAnalysisTest(unittest.TestCase):
    def test_builds_industry_growth_summary(self):
        rows = build_industry_growth_summary(
            Path("data/processed/legal_person_units_by_industry_year_panel.csv")
        )

        information = next(row for row in rows if row["industry_code"] == "information_software_it")
        self.assertEqual(information["units_2005"], 85499)
        self.assertEqual(information["units_2024"], 1896012)
        self.assertGreater(information["growth_multiple_2005_2024"], 22)

    def test_builds_transcription_quality_check(self):
        rows = build_transcription_quality_check(
            Path("data/raw/official_statistics/legal_person_units_industry_year_image_transcription.csv"),
            Path(
                "data/raw/official_statistics/"
                "legal_person_units_province_industry_2024_image_transcription.csv"
            ),
        )

        flagged = [row for row in rows if row["requires_review"]]
        row_keys = {row["row_key"] for row in flagged}
        self.assertIn("全国-2014", row_keys)
        self.assertIn("浙江省-2024", row_keys)
        self.assertIn("贵州省-2024", row_keys)


if __name__ == "__main__":
    unittest.main()
