import unittest
from pathlib import Path

from ai_scientist.demo_assets import DemoAssetBuilder


ROOT = Path(__file__).resolve().parents[1]


class DemoAssetTests(unittest.TestCase):
    def test_demo_html_export(self) -> None:
        builder = DemoAssetBuilder()
        output_path = ROOT / "results" / "test_demo_report.html"
        builder.export_html_report(
            corpus_path=ROOT / "data" / "sample_corpus.json",
            question="Do multi-agent systems improve research verification?",
            output_path=output_path,
        )
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("<html", content.lower())
        self.assertIn("AI-Scientist Demo Report", content)
        output_path.unlink()


if __name__ == "__main__":
    unittest.main()
