from __future__ import annotations

from ai_scientist.agents.retrieval import RetrievalAgent
from ai_scientist.agents.verification import VerificationAgent
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.models import ClaimAssessment, StructuredClaim
from ai_scientist.scope import DomainScopeGuard
from ai_scientist.utils import has_negation_or_limitation, overlap_score, sentence_split


class SingleAgentBaseline:
    def __init__(self, settings: Settings, corpus: CorpusRepository):
        self.settings = settings
        self.retrieval = RetrievalAgent(corpus=corpus, settings=settings)
        self.scope_guard = DomainScopeGuard(settings=settings)

    def verify_claim(self, claim: str) -> ClaimAssessment:
        structured_claim = StructuredClaim(
            text=claim,
            claim_type="baseline_query",
            source_paper_id="USER",
            source_title="User Query",
            source_sentence=claim,
            focus_terms=[],
        )
        scope = self.scope_guard.assess(claim)
        if not scope.in_scope:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="out_of_scope",
                confidence=0.0,
                evidence=[],
                rationale=self.scope_guard.out_of_scope_message(scope),
            )
        retrieved = self.retrieval.retrieve(claim, top_k=1)
        if not retrieved:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="insufficient_evidence",
                confidence=self.settings.confidence_floor,
                evidence=[],
                rationale="Single-agent baseline found no sufficiently relevant paper in the current corpus.",
            )
        top_paper = retrieved[0]
        best_sentence = ""
        best_score = 0.0

        for sentence in sentence_split(top_paper.abstract):
            score = overlap_score(claim, sentence)
            if score > best_score:
                best_score = score
                best_sentence = sentence

        if best_score >= self.settings.min_support_overlap:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="supported",
                confidence=round(min(0.8, 0.4 + best_score), 3),
                evidence=[],
                rationale=f"Direct baseline trusted the top-ranked paper: {top_paper.title}.",
            )
        return ClaimAssessment(
            claim=structured_claim,
            verdict="insufficient_evidence",
            confidence=self.settings.confidence_floor,
            evidence=[],
            rationale=f"Direct baseline could not confidently ground the claim in {top_paper.title}.",
        )


class RagBaseline:
    def __init__(self, settings: Settings, corpus: CorpusRepository):
        self.settings = settings
        self.retrieval = RetrievalAgent(corpus=corpus, settings=settings)
        self.scope_guard = DomainScopeGuard(settings=settings)

    def verify_claim(self, claim: str) -> ClaimAssessment:
        structured_claim = StructuredClaim(
            text=claim,
            claim_type="baseline_query",
            source_paper_id="USER",
            source_title="User Query",
            source_sentence=claim,
            focus_terms=[],
        )
        scope = self.scope_guard.assess(claim)
        if not scope.in_scope:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="out_of_scope",
                confidence=0.0,
                evidence=[],
                rationale=self.scope_guard.out_of_scope_message(scope),
            )
        papers = self.retrieval.retrieve(claim, top_k=self.settings.top_k_retrieval)
        if not papers:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="insufficient_evidence",
                confidence=self.settings.confidence_floor,
                evidence=[],
                rationale="RAG baseline found no sufficiently relevant papers in the current corpus.",
            )
        claim_has_negation = has_negation_or_limitation(claim, self.settings.contradiction_terms)
        best_support = 0.0
        evidence_count = 0

        for paper in papers:
            for sentence in sentence_split(paper.abstract):
                score = overlap_score(claim, sentence)
                if score < self.settings.min_support_overlap:
                    continue
                if has_negation_or_limitation(sentence, self.settings.contradiction_terms) == claim_has_negation:
                    evidence_count += 1
                    best_support = max(best_support, score)

        if evidence_count:
            return ClaimAssessment(
                claim=structured_claim,
                verdict="supported",
                confidence=round(min(0.88, 0.45 + best_support + (0.03 * (evidence_count - 1))), 3),
                evidence=[],
                rationale="RAG baseline found supporting context but does not perform explicit contradiction analysis.",
            )

        return ClaimAssessment(
            claim=structured_claim,
            verdict="insufficient_evidence",
            confidence=self.settings.confidence_floor,
            evidence=[],
            rationale="RAG baseline did not find enough aligned support in the retrieved context.",
        )
