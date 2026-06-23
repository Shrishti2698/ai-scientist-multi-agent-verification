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
        matched_non_research_terms = self._match_terms(normalized, self.settings.non_research_keywords)
        
        # Consider it research-related if:
        # 1. Has research keywords AND no clear non-research keywords, OR
        # 2. Contains question words with research context
        has_research_context = bool(matched_research_terms)
        has_question_words = any(word in normalized for word in ["does", "do", "can", "what", "how", "why", "which", "when", "where"])
        
        # Research questions often don't explicitly use "research" but ask about effects, comparisons, etc.
        research_question_patterns = [
            "effect of", "impact of", "influence of", "relationship between", "comparison", "compare",
            "versus", "vs", "better than", "improve", "reduce", "increase", "correlation", "association",
            "significant", "study show", "research show", "evidence", "findings", "results", "according to"
        ]
        has_research_patterns = any(pattern in normalized for pattern in research_question_patterns)
        
        in_scope = (
            (has_research_context or has_research_patterns or (has_question_words and len(normalized.split()) > 8))
            and not matched_non_research_terms
        )
        
        return ScopeDecision(
            in_scope=in_scope,
            matched_in_scope_terms=matched_research_terms,
            matched_out_of_scope_terms=matched_non_research_terms,
        )

    def out_of_scope_message(self, decision: ScopeDecision) -> str:
        if decision.matched_out_of_scope_terms:
            terms = ", ".join(decision.matched_out_of_scope_terms[:3])
            return (
                "Sorry, this system is designed for research-oriented questions only. "
                f"Your query appears to be about {terms}, which falls outside the research domain. "
                "Please ask a research question about any academic field for analysis."
            )
        return (
            "Sorry, this system is designed for research-oriented questions only. "
            "Please ask a research question from any academic domain (medicine, physics, psychology, "
            "computer science, biology, economics, etc.) for analysis."
        )

    def _match_terms(self, normalized_text: str, terms: tuple[str, ...]) -> list[str]:
        matches: list[str] = []
        for term in terms:
            escaped = re.escape(term.lower())
            pattern = rf"(?<!\w){escaped}(?!\w)"
            if re.search(pattern, normalized_text):
                matches.append(term)
        return matches
