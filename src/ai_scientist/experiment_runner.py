from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.baselines import RagBaseline, SingleAgentBaseline
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository, load_benchmark_cases
from ai_scientist.evaluation import Evaluator
from ai_scientist.literature import LiteratureCollectionService, LiteratureFetchError
from ai_scientist.models import EvaluationSummary


class ExperimentRunner:
    def __init__(
        self,
        settings: Settings,
        corpus_path: str | Path,
        benchmark_path: str | Path,
        live_query: str | None = None,
        live_limit_per_source: int = 5,
        live_output_path: str | Path | None = None,
    ):
        self.settings = settings
        self.corpus_path = Path(corpus_path)
        self.benchmark_path = Path(benchmark_path)
        self.corpus = CorpusRepository.from_path(self.corpus_path)
        self.cases = load_benchmark_cases(benchmark_path)
        self.evaluator = Evaluator()
        self.live_query = live_query
        self.live_limit_per_source = live_limit_per_source
        self.live_output_path = Path(live_output_path) if live_output_path else None
        self.systems = {
            "single_agent": SingleAgentBaseline(settings=settings, corpus=self.corpus),
            "rag": RagBaseline(settings=settings, corpus=self.corpus),
            "multi_agent_no_critic_loop": MultiAgentResearchSystem(
                settings=settings,
                corpus=self.corpus,
                enable_second_pass=False,
            ),
            "multi_agent": MultiAgentResearchSystem(settings=settings, corpus=self.corpus),
        }

    def refresh_corpus_from_live_sources(self) -> Path:
        if not self.live_query:
            raise ValueError("live_query is required to fetch a live corpus.")
        service = LiteratureCollectionService()
        papers = service.collect(query=self.live_query, limit_per_source=self.live_limit_per_source)
        output_path = self.live_output_path or self.corpus_path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        service.export(papers, output_path)
        self.corpus_path = output_path
        self.corpus = CorpusRepository.from_path(self.corpus_path)
        self.systems = {
            "single_agent": SingleAgentBaseline(settings=self.settings, corpus=self.corpus),
            "rag": RagBaseline(settings=self.settings, corpus=self.corpus),
            "multi_agent_no_critic_loop": MultiAgentResearchSystem(
                settings=self.settings,
                corpus=self.corpus,
                enable_second_pass=False,
            ),
            "multi_agent": MultiAgentResearchSystem(settings=self.settings, corpus=self.corpus),
        }
        return output_path

    def try_refresh_corpus_from_live_sources(self) -> tuple[bool, str]:
        try:
            path = self.refresh_corpus_from_live_sources()
            return True, f"Live corpus refreshed at {path}"
        except (LiteratureFetchError, ValueError) as exc:
            return False, str(exc)

    def run(self) -> list[EvaluationSummary]:
        return [
            self.evaluator.evaluate_system(system_name, verifier, self.cases)
            for system_name, verifier in self.systems.items()
        ]

    def export(self, output_dir: str | Path) -> list[EvaluationSummary]:
        summaries = self.run()
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)

        self._write_json(root / "summary.json", summaries)
        self._write_csv(root / "case_results.csv", summaries)
        self._write_markdown(root / "report.md", summaries)
        return summaries

    def _write_json(self, path: Path, summaries: list[EvaluationSummary]) -> None:
        payload = {
            "summaries": [
                {
                    "system_name": summary.system_name,
                    "total_cases": summary.total_cases,
                    "accuracy": summary.accuracy,
                    "average_confidence": summary.average_confidence,
                    "average_evidence_count": summary.average_evidence_count,
                    "contradiction_recall": summary.contradiction_recall,
                    "category_accuracy": summary.category_accuracy,
                    "rows": [asdict(row) for row in summary.rows],
                }
                for summary in summaries
            ]
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def _write_csv(self, path: Path, summaries: list[EvaluationSummary]) -> None:
        with path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "system_name",
                    "case_id",
                    "predicted_verdict",
                    "expected_verdict",
                    "confidence",
                    "evidence_count",
                    "is_correct",
                ],
            )
            writer.writeheader()
            for summary in summaries:
                for row in summary.rows:
                    writer.writerow(asdict(row))

    def _write_markdown(self, path: Path, summaries: list[EvaluationSummary]) -> None:
        lines = ["# Experiment Report", "", "## System Summaries"]
        for summary in summaries:
            lines.append(f"### {summary.system_name}")
            lines.append(f"- Total cases: {summary.total_cases}")
            lines.append(f"- Accuracy: {summary.accuracy}")
            lines.append(f"- Average confidence: {summary.average_confidence}")
            lines.append(f"- Average evidence count: {summary.average_evidence_count}")
            lines.append(f"- Contradiction recall: {summary.contradiction_recall}")
            if summary.category_accuracy:
                category_bits = ", ".join(
                    f"{name}={score}" for name, score in summary.category_accuracy.items()
                )
                lines.append(f"- Category accuracy: {category_bits}")
            lines.append("")

        best = max(summaries, key=lambda item: item.accuracy, default=None)
        if best is not None:
            lines.append("## Headline Finding")
            lines.append(
                f"The best accuracy in this run came from `{best.system_name}` with a score of `{best.accuracy}`."
            )
            lines.append("")

        multi_agent = next((item for item in summaries if item.system_name == "multi_agent"), None)
        ablation = next((item for item in summaries if item.system_name == "multi_agent_no_critic_loop"), None)
        if multi_agent and ablation:
            delta = round(multi_agent.accuracy - ablation.accuracy, 3)
            lines.append("## Critic Loop Ablation")
            lines.append(
                f"The critic-guided second pass changes multi-agent accuracy by `{delta}` compared to the no-loop ablation."
            )
            lines.append("")

        lines.append("## Notes")
        lines.append("These results are from the current offline benchmark and should be treated as early-stage research signals.")
        path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
