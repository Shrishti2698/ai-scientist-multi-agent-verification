from __future__ import annotations

import re
from dataclasses import dataclass

from ai_scientist.config import Settings
from ai_scientist.utils import normalize_text


@dataclass(slots=True)
class ScopeDecision:
    in_scope: bool
    matched_in_scope_terms: list[str]
    matched_out_of_scope_terms: list[str]


class DomainScopeGuard:
    def __init__(self, settings: Settings):
        self.settings = settings

    def assess(self, text: str) -> ScopeDecision:
        normalized = normalize_text(text).lower()
        matched_in_scope_terms = self._match_terms(normalized, self.settings.in_scope_keywords)
        matched_out_of_scope_terms = self._match_terms(normalized, self.settings.out_of_scope_keywords)
        in_scope = bool(matched_in_scope_terms) and not matched_out_of_scope_terms
        return ScopeDecision(
            in_scope=in_scope,
            matched_in_scope_terms=matched_in_scope_terms,
            matched_out_of_scope_terms=matched_out_of_scope_terms,
        )

    def out_of_scope_message(self, decision: ScopeDecision) -> str:
        if decision.matched_out_of_scope_terms:
            terms = ", ".join(decision.matched_out_of_scope_terms[:4])
            return (
                "Sorry - this demo is validated only for AI and computer science research questions. "
                f"Your query appears to belong to another domain ({terms}). "
                "Please ask an AI/CS research question for a reliable result."
            )
        return (
            "Sorry - this demo is validated only for AI and computer science research questions. "
            "Please ask an AI/CS research question for a reliable result."
        )

    def _match_terms(self, normalized_text: str, terms: tuple[str, ...]) -> list[str]:
        matches: list[str] = []
        for term in terms:
            escaped = re.escape(term.lower())
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, normalized_text):
                matches.append(term)
        return matches
