import unittest
from pathlib import Path

from ai_scientist.corpus import load_benchmark_cases
from ai_scientist.evaluation import Evaluator
from ai_scientist.baselines import RagBaseline
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository


ROOT = Path(__file__).resolve().parents[1]


class BenchmarkMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.cases = load_benchmark_cases(ROOT / "data" / "benchmark_claims.json")
        cls.corpus = CorpusRepository.from_path(ROOT / "data" / "sample_corpus.json")

    def test_benchmark_cases_include_metadata(self) -> None:
        self.assertGreaterEqual(len(self.cases), 12)
        self.assertTrue(all(case.category for case in self.cases))
        self.assertTrue(all(case.difficulty for case in self.cases))

    def test_evaluation_summary_includes_category_accuracy(self) -> None:
        evaluator = Evaluator()
        rag = RagBaseline(settings=Settings(), corpus=self.corpus)
        summary = evaluator.evaluate_system("rag", rag, self.cases)
        self.assertTrue(summary.category_accuracy)
        self.assertIn("retrieval", summary.category_accuracy)


if __name__ == "__main__":
    unittest.main()
