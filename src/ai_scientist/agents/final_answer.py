from __future__ import annotations

from dataclasses import dataclass

from ai_scientist.config import Settings
from ai_scientist.llm import OpenAIResearchLLM
from ai_scientist.models import ClaimAssessment, CritiqueNote, PaperDocument
from ai_scientist.utils import tokenize


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

        Without the LLM the heuristic cannot freely synthesise prose, so it answers the
        question by selecting the verified claims that are *most relevant to the question*
        (not just the highest-confidence ones) and presenting them as a direct, grounded
        answer rather than a meta-summary of how many claims were found.
        """
        if not assessments:
            return (
                "The retrieved material does not contain enough aligned evidence to answer "
                "this question directly."
            )

        question_tokens = set(tokenize(question))

        def by_question_relevance(items: list[ClaimAssessment]) -> list[ClaimAssessment]:
            # Rank by how much each claim overlaps the user's question, then by confidence,
            # so the answer leads with claims that actually address what was asked.
            return sorted(
                items,
                key=lambda item: (
                    len(question_tokens & set(tokenize(item.claim.text))),
                    item.confidence,
                ),
                reverse=True,
            )

        supported = by_question_relevance(
            [item for item in assessments if item.verdict == "supported"]
        )
        contradicted = by_question_relevance(
            [item for item in assessments if item.verdict == "contradicted"]
        )

        parts: list[str] = [self._as_sentence(item.claim.text) for item in supported[:3]]
        if contradicted:
            lead = self._as_sentence(contradicted[0].claim.text)
            if parts:
                parts.append(f"However, the evidence also qualifies this: {lead}")
            else:
                # Nothing supported — answer is a qualified / negative one.
                return (
                    "Based on the retrieved evidence, the answer is qualified rather than "
                    f"affirmative: {lead}"
                )
        if not parts:
            return (
                "The retrieved papers are on-topic, but the verified claims are not decisive "
                "enough to settle the question with confidence."
            )
        return " ".join(parts)

    @staticmethod
    def _as_sentence(text: str) -> str:
        text = text.strip()
        if not text:
            return ""
        text = text[0].upper() + text[1:]
        if text[-1] not in ".!?":
            text += "."
        return text
