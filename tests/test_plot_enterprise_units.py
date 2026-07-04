import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.visualization.plot_enterprise_units import plot_key_region_enterprise_units


class EnterpriseUnitsPlotTest(unittest.TestCase):
    def test_writes_key_region_trend_png(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "enterprise_units.png"

            plot_key_region_enterprise_units(
                Path("data/processed/enterprise_units_by_province_panel.csv"),
                output_path,
            )

            self.assertTrue(output_path.exists())
            self.assertGreater(output_path.stat().st_size, 10_000)
            with Image.open(output_path) as image:
                self.assertGreater(image.size[0], 1000)
                self.assertGreater(image.size[1], 600)


if __name__ == "__main__":
    unittest.main()
