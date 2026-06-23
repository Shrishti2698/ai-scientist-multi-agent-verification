from __future__ import annotations

from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.models import PaperDocument
from ai_scientist.utils import overlap_score


class RetrievalAgent:
    def __init__(self, corpus: CorpusRepository, settings: Settings):
        self.corpus = corpus
        self.settings = settings

    def retrieve(self, query: str, top_k: int | None = None) -> list[PaperDocument]:
        limit = top_k or self.settings.top_k_retrieval
        scored = sorted(
            (
                (
                    overlap_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}"),
                    paper,
                )
                for paper in self.corpus.all_papers()
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        filtered = [paper for score, paper in scored if score >= self.settings.min_query_relevance]
        return filtered[:limit]
