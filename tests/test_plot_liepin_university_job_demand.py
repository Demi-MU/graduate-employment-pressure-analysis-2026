import tempfile
import unittest
from pathlib import Path

from PIL import Image

from src.visualization.plot_liepin_university_job_demand import (
    FIGURE_OUTPUTS,
    plot_liepin_university_job_demand,
)


class LiepinUniversityJobDemandPlotTest(unittest.TestCase):
    def test_writes_three_report_figures(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)

            written = plot_liepin_university_job_demand(output_dir=output_dir)

            self.assertEqual(set(written.keys()), set(FIGURE_OUTPUTS.keys()))
            for group, output_path in written.items():
                self.assertEqual(output_path.parent, output_dir)
                self.assertTrue(output_path.exists(), group)
                self.assertGreater(output_path.stat().st_size, 10_000)
                with Image.open(output_path) as image:
                    self.assertGreaterEqual(image.size[0], 1000)
                    self.assertGreaterEqual(image.size[1], 650)


if __name__ == "__main__":
    unittest.main()
