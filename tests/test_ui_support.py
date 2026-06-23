import unittest
from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.ui_support import available_corpus_options, report_to_sections


ROOT = Path(__file__).resolve().parents[1]


class UiSupportTests(unittest.TestCase):
    def test_available_corpus_options_includes_frozen_demo(self) -> None:
        options = available_corpus_options(ROOT)
        self.assertIn("Final Demo Corpus", options)
        self.assertTrue(options["Final Demo Corpus"].exists())

    def test_report_to_sections_contains_expected_keys(self) -> None:
        corpus = CorpusRepository.from_path(ROOT / "data" / "final_demo_corpus.json")
        system = MultiAgentResearchSystem(settings=Settings(), corpus=corpus)
        report = system.analyze_question("Do critic-guided verification loops improve research claim checking?")
        sections = report_to_sections(report)
        self.assertIn("summary", sections)
        self.assertIn("claims", sections)
        self.assertIn("iteration_trace", sections)


if __name__ == "__main__":
    unittest.main()
