from __future__ import annotations

from ai_scientist.config import Settings
from ai_scientist.llm import OpenAIResearchLLM
from ai_scientist.models import ClaimAssessment, CritiqueNote


class SynthesisAgent:
    def __init__(self, settings: Settings):
        self.llm = OpenAIResearchLLM.from_settings(settings)

    def synthesize(self, question: str, assessments: list[ClaimAssessment], notes: list[CritiqueNote]) -> str:
        if self.llm.available:
            summary = self.llm.rewrite_summary(question=question, assessments=assessments, notes=notes)
            if summary:
                return summary

        supported = [item for item in assessments if item.verdict == "supported"]
        contradicted = [item for item in assessments if item.verdict == "contradicted"]
        insufficient = [item for item in assessments if item.verdict == "insufficient_evidence"]

        parts = [f"Research question: {question}"]
        if supported:
            parts.append(
                f"Supported findings: {len(supported)} claim(s) have meaningful evidence in the current corpus."
            )
        if contradicted:
            parts.append(
                f"Conflicting findings: {len(contradicted)} claim(s) are challenged by retrieved evidence."
            )
        if insufficient:
            parts.append(
                f"Open uncertainty: {len(insufficient)} claim(s) remain unresolved with the current evidence base."
            )
        if notes:
            parts.append("Critique summary: weakly supported or contradicted claims should be reported cautiously.")
        return " ".join(parts)
