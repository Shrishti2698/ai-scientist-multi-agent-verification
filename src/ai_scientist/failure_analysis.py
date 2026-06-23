from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path


class FailureAnalysis:
    def build_markdown(self, summary_path: str | Path, benchmark_path: str | Path) -> str:
        summary_payload = json.loads(Path(summary_path).read_text(encoding="utf-8"))
        benchmark_payload = json.loads(Path(benchmark_path).read_text(encoding="utf-8"))

        case_lookup = {item["case_id"]: item for item in benchmark_payload["benchmark_cases"]}
        lines = ["# Failure Analysis", ""]

        for summary in summary_payload["summaries"]:
            incorrect_rows = [row for row in summary["rows"] if not row["is_correct"]]
            lines.append(f"## {summary['system_name']}")
            lines.append(f"- Accuracy: {summary['accuracy']}")
            lines.append(f"- Incorrect cases: {len(incorrect_rows)}")

            category_errors: Counter[str] = Counter()
            verdict_confusions: Counter[str] = Counter()

            for row in incorrect_rows:
                case = case_lookup.get(row["case_id"], {})
                category = case.get("category", "unknown")
                category_errors[category] += 1
                verdict_confusions[f"{row['expected_verdict']} -> {row['predicted_verdict']}"] += 1

            if category_errors:
                category_bits = ", ".join(f"{name}={count}" for name, count in category_errors.most_common())
                lines.append(f"- Error categories: {category_bits}")
            if verdict_confusions:
                confusion_bits = ", ".join(f"{name}={count}" for name, count in verdict_confusions.most_common())
                lines.append(f"- Verdict confusions: {confusion_bits}")
            lines.append("")

            if incorrect_rows:
                lines.append("### Misclassified Cases")
                for row in incorrect_rows:
                    case = case_lookup.get(row["case_id"], {})
                    lines.append(f"- {row['case_id']} [{case.get('category', 'unknown')}]")
                    lines.append(f"  Claim: {case.get('claim', '')}")
                    lines.append(
                        f"  Expected: `{row['expected_verdict']}` | Predicted: `{row['predicted_verdict']}` | Confidence: `{row['confidence']}`"
                    )
                lines.append("")

        return "\n".join(lines).strip() + "\n"

    def export(self, summary_path: str | Path, benchmark_path: str | Path, output_path: str | Path) -> None:
        markdown = self.build_markdown(summary_path, benchmark_path)
        Path(output_path).write_text(markdown, encoding="utf-8")
