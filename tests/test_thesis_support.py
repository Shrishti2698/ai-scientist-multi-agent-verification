import unittest
from pathlib import Path

from ai_scientist.thesis_support import ThesisSupport


ROOT = Path(__file__).resolve().parents[1]


class ThesisSupportTests(unittest.TestCase):
    def test_thesis_assets_export(self) -> None:
        support = ThesisSupport()
        output_dir = ROOT / "results" / "test_thesis_assets"
        support.export(ROOT / "results" / "latest" / "summary.json", output_dir)
        self.assertTrue((output_dir / "results_tables.md").exists())
        self.assertTrue((output_dir / "writeup_notes.md").exists())
        self.assertTrue((output_dir / "methodology_outline.md").exists())
        self.assertTrue((output_dir / "presentation_outline.md").exists())
        for path in output_dir.iterdir():
            path.unlink()
        output_dir.rmdir()



if __name__ == "__main__":
    unittest.main()
