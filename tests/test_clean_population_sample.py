import unittest
from pathlib import Path

from src.data_cleaning.clean_population_sample import build_population_sample_age_panel


class PopulationSampleAgePanelTest(unittest.TestCase):
    def test_builds_age_panel_with_sample_shares(self):
        workbook_path = Path("data/raw/official_statistics/人口抽样调查样本数据_年度数据.xlsx")

        rows = build_population_sample_age_panel(workbook_path)

        self.assertEqual(min(row["year"] for row in rows), 2016)
        self.assertEqual(max(row["year"] for row in rows), 2024)

        row_2024_20_24 = next(
            row for row in rows if row["year"] == 2024 and row["age_group"] == "20-24岁"
        )
        self.assertAlmostEqual(row_2024_20_24["population_sample_count"], 73422)
        self.assertAlmostEqual(row_2024_20_24["total_sample_count"], 1447437)
        self.assertAlmostEqual(row_2024_20_24["age_group_share"], 73422 / 1447437)
        self.assertIn("抽样调查样本数据", row_2024_20_24["note"])

        row_2016_20_29 = next(
            row for row in rows if row["year"] == 2016 and row["age_group"] == "20-29岁"
        )
        self.assertAlmostEqual(row_2016_20_29["population_sample_count"], 79102 + 106663)
        self.assertAlmostEqual(row_2016_20_29["age_group_share"], (79102 + 106663) / 1158019)


if __name__ == "__main__":
    unittest.main()
