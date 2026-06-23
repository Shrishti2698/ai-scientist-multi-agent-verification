from __future__ import annotations

import re

from ai_scientist.config import Settings
from ai_scientist.models import ClaimAssessment, CritiqueNote, IterationDecision


class CriticAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def critique(self, assessments: list[ClaimAssessment]) -> list[CritiqueNote]:
        insufficient = [a for a in assessments if a.verdict == "insufficient_evidence"]
        low_confidence = [
            a for a in assessments
            if a.confidence < self.settings.critic_confidence_threshold
            and a.verdict != "insufficient_evidence"
        ]
        single_source = [
            a for a in assessments
            if a.verdict == "supported" and len(a.evidence) == 1
        ]
        contradicted = [a for a in assessments if a.verdict == "contradicted"]

        notes: list[CritiqueNote] = []

        if insufficient:
            titles = "; ".join(a.claim.source_title for a in insufficient)
            notes.append(CritiqueNote(
                claim="",
                severity="high",
                message=(
                    f"{len(insufficient)} claim(s) have insufficient evidence and should not be presented as settled. "
                    f"Source papers: {titles}."
                ),
            ))

        if low_confidence:
            titles = "; ".join(a.claim.source_title for a in low_confidence)
            notes.append(CritiqueNote(
                claim="",
                severity="medium",
                message=(
                    f"{len(low_confidence)} claim(s) have modest confidence (below threshold). "
                    f"Narrower query phrasing or additional retrieval may improve this. "
                    f"Source papers: {titles}."
                ),
            ))

        if single_source:
            details = []
            for a in single_source:
                ev_title = a.evidence[0].title
                if ev_title == a.claim.source_title:
                    details.append(f"'{a.claim.text[:60]}...' (from: {a.claim.source_title}) — only self-corroborated")
                else:
                    details.append(f"'{a.claim.text[:60]}...' (from: {a.claim.source_title}) — single verifier: {ev_title}")
            notes.append(CritiqueNote(
                claim="",
                severity="medium",
                message=(
                    f"{len(single_source)} claim(s) are supported by only one source and need additional corroboration. "
                    f"Details: {'; '.join(details)}."
                ),
            ))

        if contradicted:
            titles = "; ".join(
                f"{a.claim.source_title} (contradicted by: {', '.join(e.title for e in a.evidence)})"
                for a in contradicted
            )
            notes.append(CritiqueNote(
                claim="",
                severity="medium",
                message=(
                    f"{len(contradicted)} claim(s) have contradictory evidence. "
                    f"The report should explicitly describe the disagreement. "
                    f"Details: {titles}."
                ),
            ))

        return notes

    def identify_reverification_targets(self, assessments: list[ClaimAssessment]) -> list[IterationDecision]:
        decisions: list[IterationDecision] = []
        for assessment in assessments:
            lowered_claim = assessment.claim.text.lower()
            if self._is_overgeneralized_claim(lowered_claim):
                continue
            if assessment.verdict == "insufficient_evidence":
                decisions.append(
                    IterationDecision(
                        claim_text=assessment.claim.text,
                        reason="insufficient evidence after first pass",
                        follow_up_query=self._build_follow_up_query(assessment),
                    )
                )
            elif assessment.confidence < self.settings.critic_confidence_threshold:
                decisions.append(
                    IterationDecision(
                        claim_text=assessment.claim.text,
                        reason="low confidence after first pass",
                        follow_up_query=self._build_follow_up_query(assessment),
                    )
                )
            elif len(assessment.evidence) < self.settings.critic_min_evidence_count:
                decisions.append(
                    IterationDecision(
                        claim_text=assessment.claim.text,
                        reason="single-source support needs corroboration",
                        follow_up_query=self._build_follow_up_query(assessment),
                    )
                )
        return decisions

    def _build_follow_up_query(self, assessment: ClaimAssessment) -> str:
        focus_terms = " ".join(assessment.claim.focus_terms)
        contradiction_probe = ""
        lowered = assessment.claim.text.lower()
        if any(cue in lowered for cue in self.settings.contradiction_claim_cues):
            contradiction_probe = "counter evidence contradiction does not not limited"
        return " ".join(
            part
            for part in (assessment.claim.text, focus_terms, assessment.claim.source_title, contradiction_probe)
            if part.strip()
        )

    def _is_overgeneralized_claim(self, text: str) -> bool:
        for cue in self.settings.overgeneralization_cues:
            normalized_cue = cue.strip().lower()
            if not normalized_cue:
                continue
            if normalized_cue != cue.lower():
                if normalized_cue in text:
                    return True
                continue
            pattern = rf"(?<!\w){re.escape(normalized_cue)}(?!\w)"
            if re.search(pattern, text):
                return True
        return False
