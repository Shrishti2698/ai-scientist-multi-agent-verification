from __future__ import annotations

from ai_scientist.config import Settings
from ai_scientist.models import PaperDocument, StructuredClaim
from ai_scientist.utils import normalize_text, sentence_split, tokenize


class ClaimExtractionAgent:
    def __init__(self, settings: Settings):
        self.settings = settings

    def extract_claims(self, question: str, papers: list[PaperDocument]) -> list[StructuredClaim]:
        claims: list[StructuredClaim] = []
        seen: set[str] = set()
        question_terms = set(tokenize(question))

        for paper in papers:
            for sentence in sentence_split(paper.abstract):
                candidate = normalize_text(sentence)
                lowered = candidate.lower()
                candidate_terms = set(tokenize(candidate))
                if candidate in seen:
                    continue
                if any(cue in lowered for cue in self.settings.positive_cues) or question_terms.intersection(
                    candidate_terms
                ):
                    claims.append(
                        StructuredClaim(
                            text=candidate,
                            claim_type=self._classify_claim_type(lowered),
                            source_paper_id=paper.paper_id,
                            source_title=paper.title,
                            source_sentence=candidate,
                            focus_terms=sorted(question_terms.intersection(candidate_terms))[:6],
                        )
                    )
                    seen.add(candidate)
                if len(claims) >= self.settings.max_claims_per_question:
                    return claims
        return claims[: self.settings.max_claims_per_question]

    def _classify_claim_type(self, sentence: str) -> str:
        if (
            "however" in sentence
            or "limited" in sentence
            or "does not" in sentence
            or "do not" in sentence
            or "fails" in sentence
            or "unlikely" in sentence
        ):
            return "limitation"
        if "improve" in sentence or "reduce" in sentence or "enhance" in sentence or "outperform" in sentence:
            return "performance"
        if "show" in sentence or "demonstrate" in sentence or "achieve" in sentence:
            return "finding"
        if "require" in sentence or "need" in sentence or "supports" in sentence:
            return "implication"
        return "observation"
