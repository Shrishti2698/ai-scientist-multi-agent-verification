from __future__ import annotations

import json
import time
from typing import Dict, List
from urllib.parse import quote_plus
import requests
import xml.etree.ElementTree as ET

from ai_scientist.models import PaperDocument
from ai_scientist.config import Settings
from ai_scientist.utils import normalize_text


class LiveRetrievalAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.pubmed_base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        self.arxiv_base = "http://export.arxiv.org/api/query"
        
    def retrieve_live_papers(self, query: str, max_papers: int = 15) -> List[PaperDocument]:
        """Retrieve papers from live APIs across multiple databases."""
        papers = []
        
        # Try PubMed Central first (medical/life sciences)
        try:
            pubmed_papers = self._retrieve_from_pubmed(query, max_papers // 2)
            papers.extend(pubmed_papers)
        except Exception as e:
            print(f"PubMed retrieval failed: {e}")
            
        # Try arXiv (physics/math/CS)  
        try:
            arxiv_papers = self._retrieve_from_arxiv(query, max_papers // 2)
            papers.extend(arxiv_papers)
        except Exception as e:
            print(f"arXiv retrieval failed: {e}")
            
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
            'retmode': 'json'
        }
        
        response = requests.get(search_url, params=search_params, timeout=10)
        response.raise_for_status()
        search_data = response.json()
        
        paper_ids = search_data.get('esearchresult', {}).get('idlist', [])
        if not paper_ids:
            return papers
            
        # Rate limiting
        time.sleep(0.34)  # 3 requests per second limit
        
        # Step 2: Get paper details
        fetch_url = f"{self.pubmed_base}esummary.fcgi"
        fetch_params = {
            'db': 'pmc',
            'id': ','.join(paper_ids),
            'retmode': 'json'
        }
        
        response = requests.get(fetch_url, params=fetch_params, timeout=10)
        response.raise_for_status()
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
            time.sleep(0.34)  # Rate limiting
            
            fetch_url = f"{self.pubmed_base}efetch.fcgi"
            params = {
                'db': 'pmc',
                'id': paper_id,
                'retmode': 'xml'
            }
            
            response = requests.get(fetch_url, params=params, timeout=10)
            response.raise_for_status()
            
            # Parse XML to extract abstract
            root = ET.fromstring(response.content)
            
            # Look for abstract in different possible locations
            abstract_elements = (
                root.findall('.//abstract') + 
                root.findall('.//AbstractText') +
                root.findall('.//sec[@sec-type="abstract"]')
            )
            
            if abstract_elements:
                abstract_text = ' '.join([
                    elem.text or '' for elem in abstract_elements
                ])
                return abstract_text[:2000]  # Limit length
                
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