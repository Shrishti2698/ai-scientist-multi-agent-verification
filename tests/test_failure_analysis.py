import unittest
from pathlib import Path

from ai_scientist.failure_analysis import FailureAnalysis


ROOT = Path(__file__).resolve().parents[1]


class FailureAnalysisTests(unittest.TestCase):
    def test_failure_analysis_exports_markdown(self) -> None:
        analyzer = FailureAnalysis()
        output_path = ROOT / "results" / "test_failure_analysis.md"
        analyzer.export(
            summary_path=ROOT / "results" / "latest" / "summary.json",
            benchmark_path=ROOT / "data" / "benchmark_claims.json",
            output_path=output_path,
        )
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("# Failure Analysis", content)
        self.assertIn("##", content)
        output_path.unlink()


if __name__ == "__main__":
    unittest.main()
