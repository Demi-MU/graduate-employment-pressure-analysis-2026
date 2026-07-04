import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data_cleaning.clean_liepin_university_job_demand import (
    EXPECTED_GROUP_COUNTS,
    clean_liepin_university_job_demand,
)


class LiepinUniversityJobDemandCleaningTest(unittest.TestCase):
    def test_cleaned_data_has_expected_shape_and_key_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "liepin_cleaned.csv"

            df = clean_liepin_university_job_demand(output_path=output_path)

            self.assertTrue(output_path.exists())
            self.assertEqual(len(df), 40)
            self.assertEqual(
                df.groupby("indicator_group").size().to_dict(),
                EXPECTED_GROUP_COUNTS,
            )

            key_values = {
                ("education_requirement", "硕士", "2024H2"): 20.3,
                ("education_requirement", "硕士", "2025H1"): 17.4,
                ("registered_capital", "[1000万,1亿]", "2025H1"): 32.1,
                ("company_type", "私营/民营企业", "2025H1"): 47.6,
            }
            indexed = df.set_index(["indicator_group", "category", "period"])
            for key, expected_value in key_values.items():
                self.assertAlmostEqual(indexed.loc[key, "percentage"], expected_value)

    def test_percentages_are_numeric_percent_points(self):
        df = clean_liepin_university_job_demand()

        self.assertTrue(pd.api.types.is_float_dtype(df["percentage"]))
        self.assertEqual(set(df["unit"]), {"percent"})
        self.assertTrue((df["percentage"] >= 0).all())
        self.assertTrue((df["percentage"] <= 100).all())


if __name__ == "__main__":
    unittest.main()
