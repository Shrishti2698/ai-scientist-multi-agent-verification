import unittest
from pathlib import Path

from ai_scientist.thesis_exports import ThesisExportBuilder


ROOT = Path(__file__).resolve().parents[1]


class ThesisExportTests(unittest.TestCase):
    def test_thesis_assets_export(self) -> None:
        builder = ThesisExportBuilder()
        output_dir = ROOT / "results" / "test_thesis_assets"
        builder.export_all(ROOT / "results" / "latest" / "summary.json", output_dir)
        self.assertTrue((output_dir / "thesis_tables.md").exists())
        self.assertTrue((output_dir / "thesis_table.tex").exists())
        self.assertTrue((output_dir / "thesis_narrative.md").exists())
        for path in output_dir.iterdir():
            path.unlink()
        output_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
