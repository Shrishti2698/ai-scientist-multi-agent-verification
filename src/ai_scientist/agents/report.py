from __future__ import annotations

from ai_scientist.models import ClaimAssessment, CritiqueNote, FinalReport, PaperDocument


class ReportGenerationAgent:
    def build(
        self,
        question: str,
        summary: str,
        assessments: list[ClaimAssessment],
        notes: list[CritiqueNote],
        papers: list[PaperDocument],
        iteration_trace: list[str],
    ) -> FinalReport:
        lines = [f"# AI-Scientist Report", "", f"## Question", question, "", "## Executive Summary", summary, ""]

        lines.append("## Retrieved Papers")
        for paper in papers:
            lines.append(f"- {paper.title} ({paper.year})")
        lines.append("")

        lines.append("## Orchestration Trace")
        if iteration_trace:
            for item in iteration_trace:
                lines.append(f"- {item}")
        else:
            lines.append("- Single-pass analysis completed.")
        lines.append("")

        lines.append("## Claim Verification")
        if assessments:
            for item in assessments:
                lines.append(f"### Claim")
                lines.append(item.claim.text)
                lines.append(f"- Claim type: `{item.claim.claim_type}`")
                lines.append(f"- Source paper: `{item.claim.source_title}`")
                if item.claim.focus_terms:
                    lines.append(f"- Focus terms: `{', '.join(item.claim.focus_terms)}`")
                lines.append(f"- Verdict: `{item.verdict}`")
                lines.append(f"- Confidence: `{item.confidence}`")
                lines.append(f"- Rationale: {item.rationale}")
                if item.evidence:
                    lines.append("- Evidence:")
                    for snippet in item.evidence:
                        lines.append(f"  - {snippet.title}: \"{snippet.sentence}\" (overlap={snippet.overlap_score})")
                else:
                    lines.append("- Evidence: none")
                lines.append("")
        else:
            lines.append("- No claim-level verification was produced for this question.")
            lines.append("")

        lines.append("## Critique Notes")
        if notes:
            for note in notes:
                lines.append(f"- [{note.severity}] {note.message} Claim: {note.claim}")
        else:
            lines.append("- No critical issues identified in this pass.")

        markdown = "\n".join(lines).strip() + "\n"
        return FinalReport(
            question=question,
            summary=summary,
            verified_claims=assessments,
            critique_notes=notes,
            retrieved_papers=papers,
            iteration_trace=iteration_trace,
            markdown=markdown,
        )
