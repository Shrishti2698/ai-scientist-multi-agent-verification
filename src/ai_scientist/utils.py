from __future__ import annotations

import re
from collections import Counter


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "do",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "using",
    "what",
    "when",
    "which",
    "with",
}


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def sentence_split(text: str) -> list[str]:
    cleaned = normalize_text(text)
    if not cleaned:
        return []
    return [segment.strip() for segment in re.split(r"(?<=[.!?])\s+", cleaned) if segment.strip()]


def tokenize(text: str) -> list[str]:
    return [
        token
        for token in re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text.lower())
        if token not in STOPWORDS
    ]


def overlap_score(left: str, right: str) -> float:
    left_tokens = set(tokenize(left))
    right_tokens = set(tokenize(right))
    if not left_tokens or not right_tokens:
        return 0.0
    intersection = len(left_tokens & right_tokens)
    union = len(left_tokens | right_tokens)
    return intersection / union


def keyword_counts(text: str) -> Counter[str]:
    return Counter(tokenize(text))


def has_negation_or_limitation(text: str, contradiction_terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    for term in contradiction_terms:
        escaped = re.escape(term.lower())
        if " " in term:
            pattern = rf"(?<!\w){escaped}(?!\w)"
        else:
            pattern = rf"\b{escaped}\b"
        if re.search(pattern, lowered):
            return True
    return False
