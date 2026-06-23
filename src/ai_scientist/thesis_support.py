from __future__ import annotations

import json
from pathlib import Path


class ThesisSupport:
    def build_results_table_markdown(self, summary_path: str | Path) -> str:
        payload = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        lines = [
            "# Thesis Results Tables",
            "",
            "## Overall Comparison",
            "",
            "| System | Accuracy | Avg Confidence | Avg Evidence | Contradiction Recall |",
            "| --- | ---: | ---: | ---: | ---: |",
        ]
        for summary in payload["summaries"]:
            lines.append(
                f"| {summary['system_name']} | {summary['accuracy']} | {summary['average_confidence']} | "
                f"{summary['average_evidence_count']} | {summary['contradiction_recall']} |"
            )

        lines.extend(["", "## Category Accuracy", ""])
        category_names = sorted(
            {
                category
                for summary in payload["summaries"]
                for category in summary.get("category_accuracy", {}).keys()
            }
        )
        header = "| System | " + " | ".join(category_names) + " |"
        separator = "| --- | " + " | ".join("---:" for _ in category_names) + " |"
        lines.append(header)
        lines.append(separator)
        for summary in payload["summaries"]:
            values = [str(summary.get("category_accuracy", {}).get(category, "-")) for category in category_names]
            lines.append(f"| {summary['system_name']} | " + " | ".join(values) + " |")

        return "\n".join(lines).strip() + "\n"

    def build_methodology_notes(self) -> str:
        lines = [
            "# Thesis Writeup Notes",
            "",
            "## Methodology Summary",
            "- Compare `single_agent`, `rag`, `multi_agent_no_critic_loop`, and `multi_agent` on the same benchmark.",
            "- Use structured claims, evidence-aware verification, and critic-guided re-verification.",
            "- Report overall accuracy, contradiction recall, evidence count, and category-wise accuracy.",
            "",
            "## Result Discussion Prompts",
            "- Explain why the multi-agent systems outperform the simpler baselines on contradiction-heavy retrieval cases.",
            "- Discuss why the critic loop may or may not improve over the no-loop ablation on the current corpus.",
            "- Highlight that failure analysis exposes remaining weaknesses in critic-oriented contradiction cases.",
        ]
        return "\n".join(lines).strip() + "\n"

    def build_methodology_chapter_outline(self) -> str:
        lines = [
            "# Methodology Chapter Outline",
            "",
            "## 1. Problem Definition",
            "- Define scientific claim verification over AI and computer science literature.",
            "- Motivate the need for verification-aware research assistants.",
            "",
            "## 2. System Design",
            "- Describe the orchestrator and each specialized agent.",
            "- Explain the baseline systems and why they were selected.",
            "",
            "## 3. Data and Benchmark",
            "- Describe the curated corpus and benchmark claims.",
            "- Explain category labels, difficulty labels, and evaluation assumptions.",
            "",
            "## 4. Experimental Setup",
            "- Report the benchmark protocol for `single_agent`, `rag`, `multi_agent_no_critic_loop`, and `multi_agent`.",
            "- Explain the critic-loop ablation and evaluation metrics.",
            "",
            "## 5. Evaluation Metrics",
            "- Accuracy",
            "- Contradiction recall",
            "- Average evidence count",
            "- Category-wise accuracy",
            "",
            "## 6. Failure Analysis",
            "- Group errors by contradiction handling, retrieval failures, and overclaim-style generalization.",
            "",
            "## 7. Threats to Validity",
            "- Limited benchmark size",
            "- Heuristic verifier bias",
            "- Static offline corpus limitations",
        ]
        return "\n".join(lines).strip() + "\n"

    def build_presentation_outline(self) -> str:
        lines = [
            "# Presentation Outline",
            "",
            "## Slide 1: Title",
            "- AI-Scientist: A Multi-Agent Orchestrated Framework for Research Verification and Adaptive Reasoning",
            "",
            "## Slide 2: Problem",
            "- Single-pass LLM answers are fluent but often weakly verified.",
            "",
            "## Slide 3: Research Question",
            "- Does orchestration improve claim verification over single-agent and RAG baselines?",
            "",
            "## Slide 4: Architecture",
            "- Orchestrator, retrieval, claim extraction, verification, critic, synthesis, report generation.",
            "",
            "## Slide 5: Methodology",
            "- Baselines, benchmark, metrics, and ablation design.",
            "",
            "## Slide 6: Results",
            "- Show main comparison and critic-loop ablation table.",
            "",
            "## Slide 7: Failure Analysis",
            "- Discuss where retrieval and contradiction handling still fail.",
            "",
            "## Slide 8: Contribution",
            "- Domain-focused multi-agent research prototype with comparative evaluation and failure analysis.",
            "",
            "## Slide 9: Future Work",
            "- Larger real corpus, stronger verifier, live literature experiments, UI polish.",
        ]
        return "\n".join(lines).strip() + "\n"

    def export(self, summary_path: str | Path, output_dir: str | Path) -> None:
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)
        (root / "results_tables.md").write_text(
            self.build_results_table_markdown(summary_path),
            encoding="utf-8",
        )
        (root / "writeup_notes.md").write_text(
            self.build_methodology_notes(),
            encoding="utf-8",
        )
        (root / "methodology_outline.md").write_text(
            self.build_methodology_chapter_outline(),
            encoding="utf-8",
        )
        (root / "presentation_outline.md").write_text(
            self.build_presentation_outline(),
            encoding="utf-8",
        )
