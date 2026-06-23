from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository, load_benchmark_cases
from ai_scientist.evaluation import Evaluator
from ai_scientist.baselines import RagBaseline, SingleAgentBaseline


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    corpus = CorpusRepository.from_path(root / "data" / "sample_corpus.json")
    settings = Settings()
    system = MultiAgentResearchSystem(settings=settings, corpus=corpus)

    question = "Do retrieval-augmented systems reduce hallucination in language models?"
    report = system.analyze_question(question)
    print(report.markdown)

    cases = load_benchmark_cases(root / "data" / "benchmark_claims.json")
    evaluator = Evaluator()
    single_agent = SingleAgentBaseline(settings=settings, corpus=corpus)
    rag = RagBaseline(settings=settings, corpus=corpus)

    for name, verifier in (
        ("single_agent", single_agent),
        ("rag", rag),
        ("multi_agent", system),
    ):
        summary = evaluator.evaluate_system(name, verifier, cases)
        print(
            f"{summary.system_name}: accuracy={summary.accuracy}, "
            f"avg_confidence={summary.average_confidence}, "
            f"avg_evidence={summary.average_evidence_count}"
        )


if __name__ == "__main__":
    main()

