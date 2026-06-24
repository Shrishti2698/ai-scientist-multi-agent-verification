from __future__ import annotations

import logging
import os
import time
from typing import List
from urllib.parse import quote_plus
import requests
import xml.etree.ElementTree as ET

from ai_scientist.models import PaperDocument
from ai_scientist.config import Settings
from ai_scientist.utils import normalize_text

logger = logging.getLogger(__name__)


class LiveRetrievalAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.arxiv_base = "http://export.arxiv.org/api/query"
        # NCBI raises the rate limit from 3 to 10 req/s when an API key is supplied,
        # and asks callers to identify themselves via `tool` and `email`.
        self.ncbi_api_key = os.getenv("NCBI_API_KEY")
        self.ncbi_email = os.getenv("NCBI_EMAIL")
        self.ncbi_tool = os.getenv("NCBI_TOOL", "ai-scientist")
        # Tighter pacing without a key (3 req/s), looser with one (10 req/s).
        self._pubmed_delay = 0.12 if self.ncbi_api_key else 0.34

    def _ncbi_params(self, params: dict) -> dict:
        """Attach NCBI identification/auth params to an eutils request."""
        enriched = dict(params)
        enriched["tool"] = self.ncbi_tool
        if self.ncbi_email:
            enriched["email"] = self.ncbi_email
        if self.ncbi_api_key:
            enriched["api_key"] = self.ncbi_api_key
        return enriched

    def _ncbi_get(self, url: str, params: dict, *, retries: int = 3) -> requests.Response:
        """GET an eutils endpoint with exponential backoff on 429 / transient errors."""
        delay = 0.5
        last_exc: Exception | None = None
        for attempt in range(retries):
            try:
                response = requests.get(url, params=self._ncbi_params(params), timeout=10)
                if response.status_code == 429:
                    raise requests.HTTPError("429 Too Many Requests", response=response)
                response.raise_for_status()
                return response
            except requests.RequestException as exc:
                last_exc = exc
                if attempt == retries - 1:
                    break
                logger.debug("NCBI request retry %d after error: %s", attempt + 1, exc)
                time.sleep(delay)
                delay *= 2
        raise last_exc if last_exc else RuntimeError("NCBI request failed")

    def retrieve_live_papers(self, query: str, max_papers: int = 15) -> List[PaperDocument]:
        """Retrieve papers from live APIs across multiple databases."""
        papers = []
        
        # Try PubMed Central first (medical/life sciences)
        try:
            pubmed_papers = self._retrieve_from_pubmed(query, max_papers // 2)
            papers.extend(pubmed_papers)
        except Exception as e:
            logger.warning("PubMed retrieval failed: %s", e)

        # Try arXiv (physics/math/CS)
        try:
            arxiv_papers = self._retrieve_from_arxiv(query, max_papers // 2)
            papers.extend(arxiv_papers)
        except Exception as e:
            logger.warning("arXiv retrieval failed: %s", e)
            
        return papers[:max_papers]
    
    def _retrieve_from_pubmed(self, query: str, max_results: int = 10) -> List[PaperDocument]:
        """Retrieve papers from PubMed Central API."""
        papers = []
        
        # Step 1: Search for paper IDs
        search_url = f"{self.pubmed_base}esearch.fcgi"
        search_params = {
            'db': 'pmc',
            'term': query,
            'retmax': max_results,
            'retmode': 'json',
            'sort': 'relevance',  # default is by date, which surfaces off-topic recent papers
        }
        
        response = self._ncbi_get(search_url, search_params)
        search_data = response.json()

        paper_ids = search_data.get('esearchresult', {}).get('idlist', [])
        if not paper_ids:
            return papers

        # Rate limiting (key-aware)
        time.sleep(self._pubmed_delay)

        # Step 2: Get paper details
        fetch_url = f"{self.pubmed_base}esummary.fcgi"
        fetch_params = {
            'db': 'pmc',
            'id': ','.join(paper_ids),
            'retmode': 'json'
        }

        response = self._ncbi_get(fetch_url, fetch_params)
        fetch_data = response.json()
        
        # Parse results
        for paper_id, data in fetch_data.get('result', {}).items():
            if paper_id == 'uids':
                continue
                
            try:
                title = data.get('title', 'Unknown Title')
                authors = [author.get('name', '') for author in data.get('authors', [])]
                
                # Get abstract via efetch
                abstract = self._get_pubmed_abstract(paper_id)
                
                paper = PaperDocument(
                    paper_id=f"PMC_{paper_id}",
                    title=normalize_text(title),
                    abstract=normalize_text(abstract or "Abstract not available"),
                    year=int(data.get('pubdate', '2023')[:4]) if data.get('pubdate') else 2023,
                    authors=authors[:3],  # Limit authors
                    topics=self._extract_topics_from_text(f"{title} {abstract}")
                )
                papers.append(paper)
                
            except (ValueError, KeyError, TypeError):
                continue
                
        return papers
    
    def _get_pubmed_abstract(self, paper_id: str) -> str:
        """Get full abstract from PubMed."""
        try:
            time.sleep(self._pubmed_delay)  # Rate limiting (key-aware)

            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            params = {
                'db': 'pmc',
                'id': paper_id,
                'retmode': 'xml'
            }

            response = self._ncbi_get(fetch_url, params)

            # Parse XML to extract abstract
            root = ET.fromstring(response.content)

            # Look for abstract in different possible locations. In JATS/PMC XML the
            # text lives in nested <p>/<sec> children, so we must gather all descendant
            # text (itertext), not just elem.text.
            abstract_elements = (
                root.findall('.//abstract')
                + root.findall('.//AbstractText')
                + root.findall('.//sec[@sec-type="abstract"]')
            )

            for elem in abstract_elements:
                text = ' '.join(part.strip() for part in elem.itertext() if part and part.strip())
                text = normalize_text(text)
                if len(text) >= 40:  # skip empty / boilerplate matches
                    return text[:2000]
        except Exception:
            pass

        return "Abstract not available via API"
    
    def _retrieve_from_arxiv(self, query: str, max_results: int = 10) -> List[PaperDocument]:
        """Retrieve papers from arXiv API."""
        papers = []
        
        params = {
            'search_query': f'all:{quote_plus(query)}',
            'start': 0,
            'max_results': max_results,
            'sortBy': 'relevance',
            'sortOrder': 'descending'
        }
        
        response = requests.get(self.arxiv_base, params=params, timeout=15)
        response.raise_for_status()
        
        # Parse Atom XML
        root = ET.fromstring(response.content)
        
        # Namespace handling
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        
        for entry in root.findall('atom:entry', ns):
            try:
                title_elem = entry.find('atom:title', ns)
                title = title_elem.text if title_elem is not None else "Unknown Title"
                
                summary_elem = entry.find('atom:summary', ns)
                abstract = summary_elem.text if summary_elem is not None else "No abstract"
                
                # Extract publication year
                published_elem = entry.find('atom:published', ns)
                year = 2023
                if published_elem is not None:
                    try:
                        year = int(published_elem.text[:4])
                    except (ValueError, TypeError):
                        year = 2023
                
                # Extract authors
                authors = []
                for author_elem in entry.findall('atom:author', ns):
                    name_elem = author_elem.find('atom:name', ns)
                    if name_elem is not None:
                        authors.append(name_elem.text)
                
                # Extract arXiv ID
                id_elem = entry.find('atom:id', ns)
                arxiv_id = "ARXIV_UNKNOWN"
                if id_elem is not None:
                    arxiv_url = id_elem.text
                    arxiv_id = f"ARXIV_{arxiv_url.split('/')[-1]}"
                
                paper = PaperDocument(
                    paper_id=arxiv_id,
                    title=normalize_text(title),
                    abstract=normalize_text(abstract),
                    year=year,
                    authors=authors[:3],
                    topics=self._extract_topics_from_text(f"{title} {abstract}")
                )
                papers.append(paper)
                
            except (ValueError, KeyError, TypeError, AttributeError):
                continue
                
        return papers
    
    def _extract_topics_from_text(self, text: str) -> List[str]:
        """Extract topic keywords from title and abstract."""
        if not text:
            return []
            
        # Common research topic keywords
        topic_keywords = {
            'machine learning', 'deep learning', 'neural network', 'ai', 'artificial intelligence',
            'quantum', 'physics', 'chemistry', 'biology', 'medicine', 'medical', 'clinical',
            'psychology', 'economics', 'finance', 'education', 'learning', 'teaching',
            'environment', 'climate', 'energy', 'renewable', 'solar', 'wind',
            'genetics', 'dna', 'protein', 'cell', 'cancer', 'diabetes', 'therapy',
            'covid', 'virus', 'vaccine', 'drug', 'treatment', 'diagnosis',
            'computer', 'software', 'algorithm', 'data', 'analysis', 'statistics'
        }
        
        text_lower = text.lower()
        found_topics = [topic for topic in topic_keywords if topic in text_lower]
        
        return found_topics[:5]  # Limit to 5 topics