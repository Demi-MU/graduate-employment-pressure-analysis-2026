import tempfile
import unittest
from pathlib import Path

from PIL import Image

import pandas as pd

from src.visualization.plot_legal_person_units import (
    HEATMAP_INDUSTRIES,
    TREND_ENDPOINT_LABEL_YEAR,
    TREND_HIGHLIGHT_MAX_N,
    TREND_LABEL_YEAR,
    TREND_RANK_YEAR,
    TREND_TOP_N,
    format_quantity_panel_label,
    plot_industry_growth_trend,
    plot_province_industry_heatmap,
    select_trend_highlight_industries,
    select_top_industries_by_year,
)


class LegalPersonUnitsPlotTest(unittest.TestCase):
    def test_heatmap_uses_high_share_industry_instead_of_health_social_work(self):
        self.assertIn("construction", HEATMAP_INDUSTRIES)
        self.assertNotIn("health_social_work", HEATMAP_INDUSTRIES)

    def test_growth_trend_uses_top_10_industries_by_2024_units(self):
        df = pd.read_csv(
            "data/processed/legal_person_units_by_industry_year_panel.csv",
            encoding="utf-8-sig",
        )
        expected = (
            df[(df["year"] == TREND_RANK_YEAR) & (df["industry_code"] != "total")]
            .sort_values("legal_person_units", ascending=False)
            .head(10)["industry_code"]
            .tolist()
        )

        selected = select_top_industries_by_year(df)
        self.assertEqual(selected, expected)
        self.assertEqual(TREND_TOP_N, 10)
        self.assertEqual(len(selected), 10)
        self.assertNotIn("total", selected)

    def test_growth_trend_marks_2020_as_label_year(self):
        self.assertEqual(TREND_LABEL_YEAR, 2020)

    def test_growth_trend_highlights_fewer_lines_than_quantity_ranking(self):
        df = pd.read_csv(
            "data/processed/legal_person_units_by_industry_year_panel.csv",
            encoding="utf-8-sig",
        )

        ranked = select_top_industries_by_year(df)
        highlighted = select_trend_highlight_industries(df)

        self.assertLess(len(highlighted), len(ranked))
        self.assertLessEqual(len(highlighted), TREND_HIGHLIGHT_MAX_N)
        self.assertTrue(set(highlighted).issubset(set(ranked)))
        self.assertIn("wholesale_retail", highlighted)
        self.assertIn("information_software_it", highlighted)
        self.assertEqual(TREND_ENDPOINT_LABEL_YEAR, 2024)

    def test_quantity_panel_label_uses_2024_actual_units(self):
        self.assertEqual(format_quantity_panel_label(11172734), "1117")

    def test_writes_industry_growth_and_heatmap_pngs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            trend_path = Path(tmpdir) / "industry_growth.png"
            heatmap_path = Path(tmpdir) / "province_heatmap.png"

            plot_industry_growth_trend(
                Path("data/processed/legal_person_units_by_industry_year_panel.csv"),
                trend_path,
            )
            plot_province_industry_heatmap(
                Path("data/processed/legal_person_units_by_province_industry_2024.csv"),
                heatmap_path,
            )

            for output_path in [trend_path, heatmap_path]:
                self.assertTrue(output_path.exists())
                self.assertGreater(output_path.stat().st_size, 10_000)
                with Image.open(output_path) as image:
                    self.assertGreater(image.size[0], 1000)
                    self.assertGreater(image.size[1], 600)


if __name__ == "__main__":
    unittest.main()
