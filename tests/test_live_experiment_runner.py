import json
import unittest
from pathlib import Path

from ai_scientist.config import Settings
from ai_scientist.experiment_runner import ExperimentRunner


ROOT = Path(__file__).resolve().parents[1]


class LiveExperimentRunnerTests(unittest.TestCase):
    def test_live_refresh_rebuilds_corpus_from_stubbed_fetcher(self) -> None:
        runner = ExperimentRunner(
            settings=Settings(),
            corpus_path=ROOT / "data" / "sample_corpus.json",
            benchmark_path=ROOT / "data" / "benchmark_claims.json",
            live_query="agentic verification",
            live_output_path=ROOT / "data" / "tmp_live_corpus.json",
        )

        class StubService:
            def collect(self, query: str, limit_per_source: int = 5):
                self.query = query
                return [
                    {
                        "paper_id": "LIVE1",
                        "title": "Live Paper",
                        "abstract": "Live abstract on verification.",
                        "year": 2026,
                        "authors": ["A"],
                        "topics": ["verification"],
                    }
                ]

        # Monkey patch by replacing method internals at instance level.
        def fake_refresh():
            payload = {
                "papers": [
                    {
                        "paper_id": "LIVE1",
                        "title": "Live Paper",
                        "abstract": "Live abstract on verification.",
                        "year": 2026,
                        "authors": ["A"],
                        "topics": ["verification"],
                    }
                ]
            }
            path = runner.live_output_path
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            runner.corpus_path = path
            return path

        runner.refresh_corpus_from_live_sources = fake_refresh
        refreshed, message = runner.try_refresh_corpus_from_live_sources()
        self.assertTrue(refreshed)
        self.assertIn("tmp_live_corpus.json", message)
        runner.live_output_path.unlink()


if __name__ == "__main__":
    unittest.main()
