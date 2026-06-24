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
        matched_research_terms = self._match_terms(normalized, self.settings.research_keywords)
        # The system accepts research questions across all academic domains
        # (medicine, physics, psychology, economics, CS, biology, ...). It only
        # turns away clearly non-research / commercial / entertainment queries.
        matched_non_research = self._match_terms(normalized, self.settings.non_research_keywords)

        in_scope = not matched_non_research

        return ScopeDecision(
            in_scope=in_scope,
            matched_in_scope_terms=matched_research_terms,
            matched_out_of_scope_terms=matched_non_research,
        )

    def out_of_scope_message(self, decision: ScopeDecision) -> str:
        base = (
            "Sorry, this system is designed for research-oriented questions only. "
            "Please ask a research question from any academic domain (medicine, physics, "
            "psychology, computer science, biology, economics, etc.) for analysis."
        )
        if decision.matched_out_of_scope_terms:
            terms = ", ".join(decision.matched_out_of_scope_terms[:3])
            return (
                "Sorry, this system is designed for research-oriented questions only. "
                f"Your query appears to be about {terms}, which falls outside the research domain. "
                "Please ask a research question about any academic field for analysis."
            )
        return base

    def _match_terms(self, normalized_text: str, terms: tuple[str, ...]) -> list[str]:
        matches: list[str] = []
        for term in terms:
            escaped = re.escape(term.lower())
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, normalized_text):
                matches.append(term)
        return matches
