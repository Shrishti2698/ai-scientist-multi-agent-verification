from __future__ import annotations

from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.models import PaperDocument
from ai_scientist.utils import overlap_score
from ai_scientist.agents.live_retrieval import LiveRetrievalAgent


class RetrievalAgent:
    def __init__(self, corpus: CorpusRepository, settings: Settings):
        self.corpus = corpus
        self.settings = settings
        self.live_agent = LiveRetrievalAgent(settings)
        self.uploaded_papers = []  # Only uploaded papers, no base corpus

    def add_uploaded_papers(self, papers: list[PaperDocument]):
        """Add uploaded papers to the hybrid system."""
        self.uploaded_papers = papers

    def retrieve(self, query: str, top_k: int | None = None) -> list[PaperDocument]:
        limit = top_k or self.settings.top_k_retrieval
        
        # First, search uploaded papers only (no base corpus)
        uploaded_papers = self._retrieve_from_uploaded(query, limit)
        print(f"DEBUG: Found {len(uploaded_papers)} relevant uploaded papers for query: {query[:50]}...")
        
        # Always try API retrieval for hybrid approach
        if self.settings.enable_live_retrieval:
            try:
                print(f"DEBUG: Attempting API retrieval for query: {query[:50]}...")
                # Fetch papers from API
                api_papers = self.live_agent.retrieve_live_papers(
                    query, 
                    max_papers=limit * 2  # Get 2x for quality filtering
                )
                print(f"DEBUG: API returned {len(api_papers)} papers")
                
                # Quality filter API papers
                quality_filtered = self._filter_by_quality(api_papers, query)
                print(f"DEBUG: After quality filtering: {len(quality_filtered)} papers")
                
                # Combine uploaded + API papers
                all_papers = self._merge_and_rank_papers(uploaded_papers, quality_filtered, query)
                print(f"DEBUG: Final merged result: {len(all_papers)} papers")
                
                return all_papers[:limit]
                
            except Exception as e:
                print(f"DEBUG: API retrieval failed: {e}")
                return uploaded_papers
        else:
            print(f"DEBUG: Live retrieval disabled in settings")
                
        return uploaded_papers
    
    def _filter_by_quality(self, papers: list[PaperDocument], query: str) -> list[PaperDocument]:
        """Filter API papers by quality metrics to maintain accuracy."""
        quality_papers = []
        
        for paper in papers:
            quality_score = self._calculate_quality_score(paper, query)
            
            # Only include papers above quality threshold
            if quality_score >= 0.3:  # Configurable threshold
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
    
    def _merge_and_rank_papers(self, uploaded_papers: list[PaperDocument], api_papers: list[PaperDocument], query: str) -> list[PaperDocument]:
        """Merge and rank papers with preference for uploaded papers."""
        
        # Score all papers with uploaded bias
        scored_papers = []
        
        # Uploaded papers get quality bonus
        for paper in uploaded_papers:
            base_score = overlap_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}")
            quality_bonus = 0.15  # Uploaded papers get quality boost
            final_score = min(1.0, base_score + quality_bonus)
            scored_papers.append((final_score, paper, 'uploaded'))
            
        # API papers use standard scoring
        for paper in api_papers:
            # Skip if we already have this paper (by title similarity)
            if not self._is_duplicate(paper, uploaded_papers):
                base_score = overlap_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}")
                scored_papers.append((base_score, paper, 'api'))
        
        # Sort by score (descending)
        scored_papers.sort(key=lambda x: x[0], reverse=True)
        
        # Filter by relevance threshold
        filtered_papers = [
            paper for score, paper, source in scored_papers 
            if score >= self.settings.min_query_relevance
        ]
        
        return filtered_papers
    
    def _is_duplicate(self, new_paper: PaperDocument, existing_papers: list[PaperDocument]) -> bool:
        """Check if paper is duplicate based on title similarity."""
        for existing in existing_papers:
            title_similarity = overlap_score(new_paper.title.lower(), existing.title.lower())
            if title_similarity > 0.7:  # High similarity threshold
                return True
        return False
    
    def _retrieve_from_uploaded(self, query: str, limit: int) -> list[PaperDocument]:
        """Retrieve papers from uploaded papers only."""
        if not self.uploaded_papers:
            return []
            
        scored = sorted(
            (
                (
                    overlap_score(query, f"{paper.title} {paper.abstract} {' '.join(paper.topics)}"),
                    paper,
                )
                for paper in self.uploaded_papers
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        filtered = [paper for score, paper in scored if score >= self.settings.min_query_relevance]
        return filtered[:limit]
