from __future__ import annotations

import re

from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.llm import OpenAIResearchLLM
from ai_scientist.models import ClaimAssessment, EvidenceSnippet, PaperDocument, StructuredClaim
from ai_scientist.utils import has_negation_or_limitation, overlap_score, sentence_split, tokenize


class VerificationAgent:
    def __init__(self, corpus: CorpusRepository, settings: Settings):
        self.corpus = corpus
        self.settings = settings
        self.llm = OpenAIResearchLLM.from_settings(settings)

    def verify_claim(
        self,
        claim: str | StructuredClaim,
        candidate_papers: list[PaperDocument] | None = None,
        prefer_contradiction_resolution: bool = False,
    ) -> ClaimAssessment:
        claim_text = claim.text if isinstance(claim, StructuredClaim) else claim
        structured_claim = (
            claim
            if isinstance(claim, StructuredClaim)
            else StructuredClaim(
                text=claim,
                claim_type="user_query",
                source_paper_id="USER",
                source_title="User Query",
                source_sentence=claim,
                focus_terms=[],
            )
        )
        supporting: list[EvidenceSnippet] = []
        contradictory: list[EvidenceSnippet] = []
        claim_has_negation = has_negation_or_limitation(claim_text, self.settings.contradiction_terms)
        claim_terms = set(tokenize(claim_text))
        focus_terms = set(structured_claim.focus_terms)
        contradiction_cue_overlap = self._contains_contradiction_claim_cue(claim_text)
        overgeneralized_claim = self._is_overgeneralized_claim(claim_text)

        papers_to_check = candidate_papers or self.corpus.all_papers()
        for paper in papers_to_check:
            for sentence in sentence_split(paper.abstract):
                score = self._evidence_score(
                    claim_text=claim_text,
                    sentence=sentence,
                    paper=paper,
                    structured_claim=structured_claim,
                    claim_terms=claim_terms,
                    focus_terms=focus_terms,
                )
                if score <= 0:
                    continue
                snippet = EvidenceSnippet(
                    paper_id=paper.paper_id,
                    title=paper.title,
                    sentence=sentence,
                    overlap_score=round(score, 3),
                )
                sentence_has_negation = has_negation_or_limitation(sentence, self.settings.contradiction_terms)
                sentence_contradiction_cue = self._contains_contradiction_claim_cue(sentence)
                if score >= self.settings.min_support_overlap:
                    if self._is_contradictory_match(
                        claim_has_negation=claim_has_negation,
                        sentence_has_negation=sentence_has_negation,
                        claim_has_contradiction_cue=contradiction_cue_overlap,
                        sentence_has_contradiction_cue=sentence_contradiction_cue,
                    ):
                        contradictory.append(snippet)
                    else:
                        supporting.append(snippet)
                elif score >= self.settings.contradiction_overlap and self._is_contradictory_match(
                    claim_has_negation=claim_has_negation,
                    sentence_has_negation=sentence_has_negation,
                    claim_has_contradiction_cue=contradiction_cue_overlap,
                    sentence_has_contradiction_cue=sentence_contradiction_cue,
                ):
                    contradictory.append(snippet)

        supporting = sorted(supporting, key=lambda item: item.overlap_score, reverse=True)[:3]
        contradictory = sorted(contradictory, key=lambda item: item.overlap_score, reverse=True)[:3]
        contradiction_sources = {item.paper_id for item in contradictory}

        if overgeneralized_claim and not prefer_contradiction_resolution:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="insufficient_evidence",
                confidence=self.settings.confidence_floor,
                evidence=[],
                rationale=(
                    "The claim is too broad for this corpus to settle confidently without stronger corroboration or a targeted contradiction pass."
                ),
            )

        if (
            supporting
            and contradictory
            and contradictory[0].overlap_score >= supporting[0].overlap_score * 1.05
            and (
                len(contradiction_sources) >= 2
                or contradictory[0].overlap_score >= self.settings.strong_contradiction_score
            )
            and prefer_contradiction_resolution
        ):
            confidence = self._contradicted_confidence(
                structured_claim=structured_claim,
                contradictory=contradictory,
                supporting=supporting,
                mixed_evidence=True,
            )
            rationale = "Contradictory evidence is present alongside partial support."
            assessment = ClaimAssessment(
                claim=structured_claim,
                verdict="contradicted",
                confidence=confidence,
                evidence=contradictory + supporting[:1],
                rationale=rationale,
            )
            return self._maybe_refine_with_llm(assessment, supporting, contradictory)

        if len(supporting) >= 1:
            confidence = self._supported_confidence(
                structured_claim=structured_claim,
                supporting=supporting,
            )
            rationale = "Retrieved evidence aligns with the claim, with confidence weighted by evidence strength, corroboration, and source independence."
            assessment = ClaimAssessment(
                claim=structured_claim,
                verdict="supported",
                confidence=confidence,
                evidence=supporting,
                rationale=rationale,
            )
            return self._maybe_refine_with_llm(assessment, supporting, contradictory)

        if contradictory and (
            len(contradiction_sources) >= 2
            or contradictory[0].overlap_score >= self.settings.strong_contradiction_score
            or (
                prefer_contradiction_resolution
                and contradiction_cue_overlap
                and not overgeneralized_claim
                and contradictory[0].overlap_score >= 0.3
            )
        ):
            if not prefer_contradiction_resolution:
                return ClaimAssessment(
                    claim=structured_claim,
                    verdict="insufficient_evidence",
                    confidence=self.settings.confidence_floor,
                    evidence=[],
                    rationale=(
                        "The corpus contains opposing hints, but the first pass does not treat them as settled contradiction."
                    ),
                )
            confidence = self._contradicted_confidence(
                structured_claim=structured_claim,
                contradictory=contradictory,
                supporting=supporting,
                mixed_evidence=False,
            )
            rationale = "Available evidence trends against the claim."
            assessment = ClaimAssessment(
                claim=structured_claim,
                verdict="contradicted",
                confidence=confidence,
                evidence=contradictory,
                rationale=rationale,
            )
            return self._maybe_refine_with_llm(assessment, supporting, contradictory)

        assessment = ClaimAssessment(
            claim=structured_claim,
            verdict="insufficient_evidence",
            confidence=self.settings.confidence_floor,
            evidence=[],
            rationale="The corpus does not provide enough overlapping evidence for this claim.",
        )
        return self._maybe_refine_with_llm(assessment, supporting, contradictory)

    def out_of_scope_assessment(self, claim: str | StructuredClaim, rationale: str) -> ClaimAssessment:
        structured_claim = (
            claim
            if isinstance(claim, StructuredClaim)
            else StructuredClaim(
                text=claim,
                claim_type="user_query",
                source_paper_id="USER",
                source_title="User Query",
                source_sentence=claim,
                focus_terms=[],
            )
        )
        return ClaimAssessment(
            claim=structured_claim,
            verdict="out_of_scope",
            confidence=0.0,
            evidence=[],
            rationale=rationale,
        )

    def _clamp_confidence(self, score: float) -> float:
        return round(max(self.settings.confidence_floor, min(self.settings.confidence_ceiling, score)), 3)

    def _supported_confidence(
        self,
        structured_claim: StructuredClaim,
        supporting: list[EvidenceSnippet],
    ) -> float:
        top_overlap = supporting[0].overlap_score
        unique_sources = {item.paper_id for item in supporting}
        independent_sources = {paper_id for paper_id in unique_sources if paper_id != structured_claim.source_paper_id}
        additional_evidence = max(0, len(supporting) - 1)
        claim_type_bonus = self._claim_type_confidence_adjustment(structured_claim.claim_type)
        same_source_only = (
            structured_claim.source_paper_id != "USER"
            and unique_sources == {structured_claim.source_paper_id}
        )

        score = (
            0.44
            + (0.18 * top_overlap)
            + (0.025 * additional_evidence)
            + (0.04 * len(independent_sources))
            + claim_type_bonus
        )
        if same_source_only:
            score -= 0.07
            score = min(score, 0.82)
        score = min(score, self.settings.confidence_ceiling - 0.03)
        return self._clamp_confidence(score)

    def _contradicted_confidence(
        self,
        structured_claim: StructuredClaim,
        contradictory: list[EvidenceSnippet],
        supporting: list[EvidenceSnippet],
        mixed_evidence: bool,
    ) -> float:
        top_overlap = contradictory[0].overlap_score
        contradiction_sources = {item.paper_id for item in contradictory}
        independent_sources = {paper_id for paper_id in contradiction_sources if paper_id != structured_claim.source_paper_id}
        claim_type_bonus = 0.02 if structured_claim.claim_type == "limitation" else 0.0
        score = (
            0.4
            + (0.17 * top_overlap)
            + (0.04 * max(0, len(contradictory) - 1))
            + (0.03 * len(independent_sources))
            + claim_type_bonus
        )
        if mixed_evidence:
            score -= 0.03 * min(len(supporting), 2)
        score = min(score, self.settings.confidence_ceiling - 0.04)
        return self._clamp_confidence(score)

    def _claim_type_confidence_adjustment(self, claim_type: str) -> float:
        adjustments = {
            "performance": 0.03,
            "finding": 0.02,
            "implication": 0.0,
            "observation": -0.02,
            "limitation": -0.03,
            "baseline_query": -0.01,
            "user_query": -0.01,
        }
        return adjustments.get(claim_type, 0.0)

    def _evidence_score(
        self,
        claim_text: str,
        sentence: str,
        paper: PaperDocument,
        structured_claim: StructuredClaim,
        claim_terms: set[str],
        focus_terms: set[str],
    ) -> float:
        base_score = overlap_score(claim_text, sentence)
        if base_score <= 0:
            return 0.0

        sentence_terms = set(tokenize(sentence))
        focus_overlap = len(focus_terms & sentence_terms) / max(1, len(focus_terms)) if focus_terms else 0.0
        term_overlap = len(claim_terms & sentence_terms) / max(1, len(claim_terms))
        source_bonus = 0.06 if paper.paper_id == structured_claim.source_paper_id else 0.0
        type_bonus = 0.04 if structured_claim.claim_type == "limitation" and has_negation_or_limitation(sentence, self.settings.contradiction_terms) else 0.0
        contradiction_cue_bonus = 0.08 if self._contains_contradiction_claim_cue(sentence) and self._contains_contradiction_claim_cue(claim_text) else 0.0

        score = base_score + (0.14 * focus_overlap) + (0.1 * term_overlap) + source_bonus + type_bonus + contradiction_cue_bonus
        return round(min(score, 1.0), 3)

    def _contains_contradiction_claim_cue(self, text: str) -> bool:
        lowered = text.lower()
        return any(cue in lowered for cue in self.settings.contradiction_claim_cues)

    def _is_contradictory_match(
        self,
        claim_has_negation: bool,
        sentence_has_negation: bool,
        claim_has_contradiction_cue: bool,
        sentence_has_contradiction_cue: bool,
    ) -> bool:
        if claim_has_negation != sentence_has_negation:
            return True
        if claim_has_contradiction_cue and sentence_has_contradiction_cue:
            return False
        if claim_has_contradiction_cue != sentence_has_contradiction_cue:
            return True
        return False

    def _is_overgeneralized_claim(self, text: str) -> bool:
        lowered = text.lower()
        for cue in self.settings.overgeneralization_cues:
            normalized_cue = cue.strip().lower()
            if not normalized_cue:
                continue
            if normalized_cue != cue.lower():
                if normalized_cue in lowered:
                    return True
                continue
            pattern = rf"(?<!\w){re.escape(normalized_cue)}(?!\w)"
            if re.search(pattern, lowered):
                return True
        return False

    def _maybe_refine_with_llm(
        self,
        assessment: ClaimAssessment,
        supporting: list[EvidenceSnippet],
        contradictory: list[EvidenceSnippet],
    ) -> ClaimAssessment:
        if not self.llm.available:
            return assessment
        refined = self.llm.refine_verification(
            claim=assessment.claim,
            preliminary=assessment,
            supporting=supporting,
            contradictory=contradictory,
        )
        return refined or assessment
