import unittest
from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.baselines import RagBaseline, SingleAgentBaseline
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository, load_benchmark_cases
from ai_scientist.evaluation import Evaluator


ROOT = Path(__file__).resolve().parents[1]


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.settings = Settings()
        cls.corpus = CorpusRepository.from_path(ROOT / "data" / "sample_corpus.json")
        cls.system = MultiAgentResearchSystem(settings=cls.settings, corpus=cls.corpus)
        cls.single_agent = SingleAgentBaseline(settings=cls.settings, corpus=cls.corpus)
        cls.rag = RagBaseline(settings=cls.settings, corpus=cls.corpus)
        cls.cases = load_benchmark_cases(ROOT / "data" / "benchmark_claims.json")

    def test_multi_agent_generates_report(self) -> None:
        report = self.system.analyze_question(
            "Do multi-agent pipelines improve scientific verification quality?"
        )
        self.assertTrue(report.summary)
        self.assertTrue(report.retrieved_papers)
        self.assertIn("# AI-Scientist Report", report.markdown)

    def test_supported_claim_is_verified(self) -> None:
        result = self.system.verify_claim(
            "Retrieval-augmented generation improves factual grounding in large language models."
        )
        self.assertEqual(result.verdict, "supported")
        self.assertGreaterEqual(len(result.evidence), 1)

    def test_multi_agent_reasoning_claim_stays_supported(self) -> None:
        result = self.system.verify_claim(
            "Multi-agent reasoning improves evidence coverage on knowledge-intensive tasks."
        )
        self.assertEqual(result.verdict, "supported")

    def test_overbroad_agentic_claim_stays_uncertain(self) -> None:
        result = self.system.verify_claim(
            "This corpus proves that agentic systems solve all factual errors."
        )
        self.assertEqual(result.verdict, "insufficient_evidence")

    def test_analysis_returns_structured_claims(self) -> None:
        report = self.system.analyze_question(
            "Do retrieval-augmented systems reduce hallucination in language models?"
        )
        self.assertTrue(report.verified_claims)
        first_claim = report.verified_claims[0].claim
        self.assertTrue(first_claim.text)
        self.assertTrue(first_claim.claim_type)
        self.assertTrue(first_claim.source_title)

    def test_analysis_records_iterative_trace(self) -> None:
        report = self.system.analyze_question(
            "Do retrieval-augmented systems reduce hallucination in language models?"
        )
        self.assertTrue(report.iteration_trace)
        self.assertTrue(any("Pass 2" in item for item in report.iteration_trace))

    def test_supported_confidence_is_not_always_ceiling(self) -> None:
        result = self.system.verify_claim(
            "Retrieval-augmented generation improves factual grounding in large language models."
        )
        self.assertEqual(result.verdict, "supported")
        self.assertLess(result.confidence, self.settings.confidence_ceiling)

    def test_report_confidences_show_variation(self) -> None:
        report = self.system.analyze_question(
            "Do critic-guided verification loops improve research claim checking?"
        )
        confidences = {item.confidence for item in report.verified_claims}
        self.assertGreater(len(confidences), 1)

    def test_out_of_scope_medical_question_stops_early(self) -> None:
        report = self.system.analyze_question(
            "What is the best treatment for diabetes according to recent research?"
        )
        self.assertFalse(report.verified_claims)
        self.assertFalse(report.retrieved_papers)
        self.assertIn("validated only for AI and computer science", report.summary)

    def test_mixed_domain_judicial_ai_question_is_rejected(self) -> None:
        report = self.system.analyze_question(
            "What does recent research say about bias in judicial AI systems?"
        )
        self.assertFalse(report.verified_claims)
        self.assertFalse(report.retrieved_papers)
        self.assertIn("judicial", report.summary.lower())

    def test_out_of_scope_claim_returns_explicit_scope_verdict(self) -> None:
        result = self.system.verify_claim(
            "Which medicine is most effective for diabetes treatment?"
        )
        self.assertEqual(result.verdict, "out_of_scope")
        self.assertEqual(result.confidence, 0.0)

    def test_baselines_reject_out_of_scope_claims(self) -> None:
        claim = "How should courts interpret constitutional contracts in modern law?"
        self.assertEqual(self.single_agent.verify_claim(claim).verdict, "out_of_scope")
        self.assertEqual(self.rag.verify_claim(claim).verdict, "out_of_scope")

    def test_evaluation_runs_for_all_systems(self) -> None:
        evaluator = Evaluator()
        summaries = [
            evaluator.evaluate_system("single_agent", self.single_agent, self.cases),
            evaluator.evaluate_system("rag", self.rag, self.cases),
            evaluator.evaluate_system("multi_agent", self.system, self.cases),
        ]
        self.assertEqual(len(summaries), 3)
        for summary in summaries:
            self.assertEqual(summary.total_cases, len(self.cases))

    def test_direct_claim_verification_uses_critic_loop_path(self) -> None:
        system = MultiAgentResearchSystem(settings=self.settings, corpus=self.corpus, enable_second_pass=True)
        result = system.verify_claim("Direct prompting alone is sufficient for scientific verification.")
        self.assertEqual(result.verdict, "contradicted")

    def test_critic_loop_recovers_strong_contradiction_claim(self) -> None:
        no_loop = MultiAgentResearchSystem(settings=self.settings, corpus=self.corpus, enable_second_pass=False)
        with_loop = MultiAgentResearchSystem(settings=self.settings, corpus=self.corpus, enable_second_pass=True)
        claim = "Critic stages eliminate all factual errors in research assistants."
        self.assertEqual(no_loop.verify_claim(claim).verdict, "insufficient_evidence")
        self.assertEqual(with_loop.verify_claim(claim).verdict, "contradicted")


if __name__ == "__main__":
    unittest.main()
