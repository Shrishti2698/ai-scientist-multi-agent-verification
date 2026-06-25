from __future__ import annotations

import logging

from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.models import PaperDocument
from ai_scientist.utils import coverage_score, overlap_score
from ai_scientist.agents.live_retrieval import LiveRetrievalAgent

logger = logging.getLogger(__name__)


class RetrievalAgent:
    def __init__(self, corpus: CorpusRepository, settings: Settings):
        self.corpus = corpus
        self.settings = settings
        self.live_agent = LiveRetrievalAgent(settings)
        self.uploaded_papers = []  # Extra papers supplied at runtime (e.g. UI uploads)

    def add_uploaded_papers(self, papers: list[PaperDocument]):
        """Register uploaded papers as part of the local retrieval pool."""
        self.uploaded_papers = papers

    def _local_pool(self) -> list[PaperDocument]:
        """The always-available grounding: uploaded papers first, then curated corpus (deduped).

        Uploaded papers are listed first so that on a tie they win de-duplication.
        """
        pool: list[PaperDocument] = []
        seen: set[str] = set()
        for paper in list(self.uploaded_papers) + list(self.corpus.all_papers()):
            if paper.paper_id in seen:
                continue
            seen.add(paper.paper_id)
            pool.append(paper)
        return pool

    def _uploaded_ids(self) -> set[str]:
        return {paper.paper_id for paper in self.uploaded_papers}

    def _local_rank_score(self, paper: PaperDocument, query: str, uploaded_ids: set[str]) -> float:
        """Coverage plus a source bonus: uploaded papers outrank corpus papers."""
        base = coverage_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}")
        bonus = (
            self.settings.uploaded_paper_quality_bonus
            if paper.paper_id in uploaded_ids
            else self.settings.local_paper_quality_bonus
        )
        return min(1.0, base + bonus)

    def _live_rank_score(self, paper: PaperDocument, query: str) -> float:
        """Blend live-paper relevance and quality so good live hits can surface."""
        base = coverage_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}")
        quality = self._calculate_quality_score(paper, query)
        blended = (base * 0.7) + (quality * 0.3)
        return min(1.0, blended + self.settings.live_paper_quality_bonus)

    def retrieve(self, query: str, top_k: int | None = None) -> list[PaperDocument]:
        limit = top_k or self.settings.top_k_retrieval

        # Local corpus + uploads are the deterministic, always-available grounding.
        local_papers = self._retrieve_from_local(query, max(limit * 4, limit))
        logger.debug("Found %d relevant local paper(s) for query: %.50s", len(local_papers), query)

        # Live API retrieval is optional augmentation layered on top of the local pool.
        if self.settings.enable_live_retrieval:
            try:
                api_papers = self.live_agent.retrieve_live_papers(query, max_papers=max(limit * 4, limit * 2))
                logger.debug("API returned %d paper(s)", len(api_papers))

                quality_filtered = self._filter_by_quality(api_papers, query)
                if not quality_filtered and api_papers:
                    quality_filtered = sorted(
                        api_papers,
                        key=lambda paper: self._calculate_quality_score(paper, query),
                        reverse=True,
                    )[: max(1, limit)]
                logger.debug("After quality filtering: %d paper(s)", len(quality_filtered))

                all_papers = self._merge_and_rank_papers(local_papers, quality_filtered, query)
                logger.debug("Final merged result: %d paper(s)", len(all_papers))
                return all_papers[:limit]
            except Exception as exc:  # pragma: no cover - network failure path
                logger.warning("Live API retrieval failed, falling back to local pool: %s", exc)
                return local_papers
        return local_papers

    def _filter_by_quality(self, papers: list[PaperDocument], query: str) -> list[PaperDocument]:
        """Filter API papers by quality metrics to maintain accuracy."""
        quality_papers = []
        
        for paper in papers:
            quality_score = self._calculate_quality_score(paper, query)
            
            # Only include papers above quality threshold
            if quality_score >= self.settings.live_paper_quality_threshold:
                quality_papers.append(paper)
                
        return quality_papers
    
    def _calculate_quality_score(self, paper: PaperDocument, query: str) -> float:
        """Calculate quality score for a paper based on multiple factors."""
        score = 0.0
        
        # Abstract length (papers with very short abstracts are low quality)
        abstract_length = len(paper.abstract.split())
        if abstract_length >= 50:  # Good length
            score += 0.3
        elif abstract_length >= 20:  # Acceptable
            score += 0.15
            
        # Title relevance to query
        title_relevance = overlap_score(query.lower(), paper.title.lower())
        score += title_relevance * 0.4
        
        # Abstract relevance to query  
        abstract_relevance = overlap_score(query.lower(), paper.abstract.lower())
        score += abstract_relevance * 0.4
        
        # Recency bonus (newer papers often higher quality)
        if paper.year >= 2020:
            score += 0.1
        elif paper.year >= 2015:
            score += 0.05
            
        # Has authors (indicates proper metadata)
        if paper.authors:
            score += 0.1
            
        # Abstract contains research indicators
        research_indicators = ['study', 'analysis', 'results', 'findings', 'method', 'conclusion']
        indicator_count = sum(1 for indicator in research_indicators if indicator in paper.abstract.lower())
        score += min(0.2, indicator_count * 0.05)
        
        return min(1.0, score)
    
    def _merge_and_rank_papers(self, local_papers: list[PaperDocument], api_papers: list[PaperDocument], query: str) -> list[PaperDocument]:
        """Merge and rank papers, preferring curated local/uploaded papers."""

        # Score all papers with a bias toward the curated local pool.
        scored_papers = []

        # Local papers (uploads + corpus) get a quality bonus; uploads rank highest.
        uploaded_ids = self._uploaded_ids()
        for paper in local_papers:
            final_score = self._local_rank_score(paper, query, uploaded_ids)
            scored_papers.append((final_score, paper, 'local'))

        # API papers use live-source scoring so high-quality live results can surface.
        for paper in api_papers:
            # Skip if we already have this paper (by title similarity)
            if not self._is_duplicate(paper, local_papers):
                live_score = self._live_rank_score(paper, query)
                scored_papers.append((live_score, paper, 'api'))
        
        # Sort by score (descending)
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        
        # Filter by coverage threshold
        filtered_papers = [
            paper for score, paper, source in scored_papers
            if score >= self.settings.min_query_coverage
        ]
        
        return filtered_papers
    
    def _is_duplicate(self, new_paper: PaperDocument, existing_papers: list[PaperDocument]) -> bool:
        """Check if paper is duplicate based on title similarity."""
        for existing in existing_papers:
            title_similarity = overlap_score(new_paper.title.lower(), existing.title.lower())
            if title_similarity > 0.7:  # High similarity threshold
                return True
        return False
    
    def _retrieve_from_local(self, query: str, limit: int) -> list[PaperDocument]:
        """Retrieve papers from the local pool (curated corpus + uploaded papers)."""
        local_pool = self._local_pool()
        if not local_pool:
            return []

        uploaded_ids = self._uploaded_ids()
        scored = sorted(
            (
                (
                    self._local_rank_score(paper, query, uploaded_ids),
                    coverage_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}"),
                    paper,
                )
                for paper in local_pool
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        # Rank by the source-weighted score, but gate on raw query coverage so a
        # source bonus alone cannot pull in an irrelevant paper.
        filtered = [paper for _rank, coverage, paper in scored if coverage >= self.settings.min_query_coverage]
        return filtered[:limit]
