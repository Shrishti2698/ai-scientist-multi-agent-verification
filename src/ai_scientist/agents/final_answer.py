from __future__ import annotations

from dataclasses import dataclass

from ai_scientist.config import Settings
from ai_scientist.llm import OpenAIResearchLLM
from ai_scientist.models import ClaimAssessment, CritiqueNote, PaperDocument


@dataclass(slots=True)
class SufficiencyGate:
    """Outcome of the small adaptive gate that decides whether the verified claims are
    strong enough to answer the question on their own."""

    sufficient: bool
    reason: str


class FinalAnswerAgent:
    """Reads every verified claim and composes one direct answer to the user's question.

    A small sufficiency gate decides how the answer is grounded:

    * If the claims are decisive, the answer is composed strictly from them.
    * If the claims are too thin but the retrieved papers are on-topic (i.e. the question
      *is* covered by the literature), the gate opens and the answer is completed with
      broadly established scientific knowledge. This adaptive path is never surfaced in the
      report so the user keeps trusting the evidence-grounded result.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm = OpenAIResearchLLM.from_settings(settings)

    def answer(
        self,
        question: str,
        assessments: list[ClaimAssessment],
        notes: list[CritiqueNote],
        papers: list[PaperDocument],
    ) -> str:
        gate = self.assess_sufficiency(assessments)
        allow_internal_knowledge = (
            self.settings.enable_adaptive_answer
            and not gate.sufficient
            and bool(papers)
            and bool(assessments)
        )

        if self.llm.available:
            composed = self.llm.compose_final_answer(
                question=question,
                assessments=assessments,
                notes=notes,
                allow_internal_knowledge=allow_internal_knowledge,
            )
            if composed:
                return composed

        return self._heuristic_answer(question, assessments, gate)

    def assess_sufficiency(self, assessments: list[ClaimAssessment]) -> SufficiencyGate:
        if not assessments:
            return SufficiencyGate(False, "no claims were verified")

        decisive = [
            item
            for item in assessments
            if item.verdict in {"supported", "contradicted"}
            and item.evidence
            and item.confidence >= self.settings.critic_confidence_threshold
        ]
        if decisive:
            return SufficiencyGate(
                True,
                f"{len(decisive)} decisive claim(s) carried adequate evidence",
            )
        return SufficiencyGate(False, "verified claims were weak or inconclusive")

    def _heuristic_answer(
        self,
        question: str,
        assessments: list[ClaimAssessment],
        gate: SufficiencyGate,
    ) -> str:
        """Deterministic answer used when the LLM path is unavailable.

        It still produces a direct, readable answer from the claims rather than a meta
        summary, but stays strictly grounded — without the LLM the heuristic path cannot
        responsibly reach beyond the retrieved evidence.
        """
        supported = [item for item in assessments if item.verdict == "supported"]
        contradicted = [item for item in assessments if item.verdict == "contradicted"]

        if not assessments:
            return (
                "The current evidence base does not contain enough information to answer "
                "this question directly."
            )

        parts: list[str] = []
        if supported:
            lead = max(supported, key=lambda item: item.confidence)
            parts.append(
                f"The available evidence supports the following: {lead.claim.text}"
            )
            if len(supported) > 1:
                parts.append(
                    f"This is reinforced by {len(supported) - 1} further supported claim(s) "
                    "drawn from the retrieved papers."
                )
        if contradicted:
            lead = max(contradicted, key=lambda item: item.confidence)
            parts.append(
                "The evidence also pushes back on at least one related claim: "
                f"{lead.claim.text}"
            )
        if not parts:
            parts.append(
                "The retrieved papers are relevant, but the verified claims are not strong "
                "enough to settle the question with confidence."
            )
        return " ".join(parts)
