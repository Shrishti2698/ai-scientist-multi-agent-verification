from __future__ import annotations

from collections import defaultdict

from ai_scientist.models import BenchmarkCase, EvaluationRow, EvaluationSummary


class Evaluator:
    def evaluate_system(self, system_name: str, verifier, cases: list[BenchmarkCase]) -> EvaluationSummary:
        rows: list[EvaluationRow] = []
        contradiction_cases = 0
        contradiction_hits = 0
        category_totals: dict[str, int] = defaultdict(int)
        category_hits: dict[str, int] = defaultdict(int)

        for case in cases:
            assessment = verifier.verify_claim(case.claim)
            is_correct = assessment.verdict == case.expected_verdict
            category_totals[case.category] += 1
            if is_correct:
                category_hits[case.category] += 1
            if case.expected_verdict == "contradicted":
                contradiction_cases += 1
                if assessment.verdict == "contradicted":
                    contradiction_hits += 1

            rows.append(
                EvaluationRow(
                    system_name=system_name,
                    case_id=case.case_id,
                    predicted_verdict=assessment.verdict,
                    expected_verdict=case.expected_verdict,
                    confidence=assessment.confidence,
                    evidence_count=len(assessment.evidence),
                    is_correct=is_correct,
                )
            )

        total = len(rows) or 1
        accuracy = sum(1 for row in rows if row.is_correct) / total
        average_confidence = sum(row.confidence for row in rows) / total
        average_evidence_count = sum(row.evidence_count for row in rows) / total
        contradiction_recall = contradiction_hits / contradiction_cases if contradiction_cases else 0.0
        category_accuracy = {
            category: round(category_hits[category] / count, 3)
            for category, count in sorted(category_totals.items())
        }

        return EvaluationSummary(
            system_name=system_name,
            total_cases=len(rows),
            accuracy=round(accuracy, 3),
            average_confidence=round(average_confidence, 3),
            average_evidence_count=round(average_evidence_count, 3),
            contradiction_recall=round(contradiction_recall, 3),
            category_accuracy=category_accuracy,
            rows=rows,
        )
