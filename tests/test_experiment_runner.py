import json
import unittest
from pathlib import Path

from ai_scientist.config import Settings
from ai_scientist.experiment_runner import ExperimentRunner


ROOT = Path(__file__).resolve().parents[1]


class ExperimentRunnerTests(unittest.TestCase):
    def test_export_creates_result_artifacts(self) -> None:
        output_dir = ROOT / "results" / "test_run"
        runner = ExperimentRunner(
            settings=Settings(),
            corpus_path=ROOT / "data" / "sample_corpus.json",
            benchmark_path=ROOT / "data" / "benchmark_claims.json",
        )
        summaries = runner.export(output_dir)

        self.assertEqual(len(summaries), 4)
        self.assertTrue((output_dir / "summary.json").exists())
        self.assertTrue((output_dir / "case_results.csv").exists())
        self.assertTrue((output_dir / "report.md").exists())

        payload = json.loads((output_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(len(payload["summaries"]), 4)
        system_names = {item["system_name"] for item in payload["summaries"]}
        self.assertIn("multi_agent_no_critic_loop", system_names)

        for path in output_dir.iterdir():
            path.unlink()
        output_dir.rmdir()


if __name__ == "__main__":
    unittest.main()
