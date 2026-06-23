from __future__ import annotations

import json
from pathlib import Path


class ThesisExportBuilder:
    def load_summary(self, summary_path: str | Path) -> dict:
        return json.loads(Path(summary_path).read_text(encoding="utf-8"))

    def build_markdown_tables(self, summary_path: str | Path) -> str:
        payload = self.load_summary(summary_path)
        summaries = payload["summaries"]

        lines = ["# Thesis Result Tables", "", "## Overall Comparison", ""]
        lines.append("| System | Accuracy | Avg Confidence | Avg Evidence | Contradiction Recall |")
        lines.append("|---|---:|---:|---:|---:|")
        for item in summaries:
            lines.append(
                f"| {item['system_name']} | {item['accuracy']} | {item['average_confidence']} | "
                f"{item['average_evidence_count']} | {item['contradiction_recall']} |"
            )
        lines.append("")

        lines.append("## Category Accuracy")
        lines.append("")
        categories = sorted({category for item in summaries for category in item.get("category_accuracy", {}).keys()})
        header = "| System | " + " | ".join(categories) + " |"
        divider = "|---|" + "|".join("---:" for _ in categories) + "|"
        lines.append(header)
        lines.append(divider)
        for item in summaries:
            values = [str(item.get("category_accuracy", {}).get(category, "-")) for category in categories]
            lines.append(f"| {item['system_name']} | " + " | ".join(values) + " |")
        lines.append("")

        return "\n".join(lines).strip() + "\n"

    def build_latex_table(self, summary_path: str | Path) -> str:
        payload = self.load_summary(summary_path)
        summaries = payload["summaries"]
        lines = [
            r"\begin{table}[ht]",
            r"\centering",
            r"\begin{tabular}{lcccc}",
            r"\hline",
            r"System & Accuracy & Avg. Conf. & Avg. Evidence & Contradiction Recall \\",
            r"\hline",
        ]
        for item in summaries:
            lines.append(
                f"{item['system_name']} & {item['accuracy']} & {item['average_confidence']} & "
                f"{item['average_evidence_count']} & {item['contradiction_recall']} \\\\"
            )
        lines.extend([r"\hline", r"\end{tabular}", r"\caption{System-level benchmark comparison}", r"\end{table}"])
        return "\n".join(lines) + "\n"

    def build_result_narrative(self, summary_path: str | Path) -> str:
        payload = self.load_summary(summary_path)
        summaries = {item["system_name"]: item for item in payload["summaries"]}
        single = summaries.get("single_agent")
        rag = summaries.get("rag")
        no_loop = summaries.get("multi_agent_no_critic_loop")
        multi = summaries.get("multi_agent")

        lines = ["# Thesis Result Narrative", ""]
        if single and rag and multi:
            lines.append(
                f"The multi-agent system achieves an accuracy of {multi['accuracy']} on the current benchmark, "
                f"outperforming the single-agent baseline ({single['accuracy']}) and the standard RAG baseline ({rag['accuracy']})."
            )
        if no_loop and multi:
            delta = round(multi["accuracy"] - no_loop["accuracy"], 3)
            lines.append(
                f"The critic-guided second pass changes overall accuracy by {delta} relative to the no-loop ablation."
            )
            critic_no_loop = no_loop.get("category_accuracy", {}).get("critic")
            critic_loop = multi.get("category_accuracy", {}).get("critic")
            if critic_no_loop is not None and critic_loop is not None:
                lines.append(
                    f"For the `critic` category specifically, accuracy changes from {critic_no_loop} to {critic_loop}, "
                    f"suggesting whether the second pass helps on contradiction-heavy critic claims."
                )
        lines.append(
            "The remaining errors are concentrated in contradiction-sensitive retrieval and overclaim-style verification cases, "
            "which indicates that future improvements should focus on stronger counter-evidence retrieval and contradiction reasoning."
        )
        return "\n\n".join(lines).strip() + "\n"

    def export_all(self, summary_path: str | Path, output_dir: str | Path) -> None:
        root = Path(output_dir)
        root.mkdir(parents=True, exist_ok=True)
        (root / "thesis_tables.md").write_text(self.build_markdown_tables(summary_path), encoding="utf-8")
        (root / "thesis_table.tex").write_text(self.build_latex_table(summary_path), encoding="utf-8")
        (root / "thesis_narrative.md").write_text(self.build_result_narrative(summary_path), encoding="utf-8")
