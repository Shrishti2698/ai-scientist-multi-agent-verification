from __future__ import annotations

import json
import os
import ssl
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import asdict
from pathlib import Path

from ai_scientist.models import PaperDocument
from ai_scientist.utils import normalize_text


class LiteratureFetchError(RuntimeError):
    """Raised when external literature retrieval fails."""


class SemanticScholarFetcher:
    BASE_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search(self, query: str, limit: int = 5) -> list[PaperDocument]:
        params = {
            "query": query,
            "limit": str(limit),
            "fields": "title,abstract,year,authors,fieldsOfStudy",
        }
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        headers = {"User-Agent": "AI-Scientist/0.1"}

        api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
        if api_key:
            headers["x-api-key"] = api_key

        payload = self._get_json(url, headers=headers)
        papers: list[PaperDocument] = []
        for item in payload.get("data", []):
            abstract = normalize_text(item.get("abstract") or "")
            if not item.get("title") or not abstract:
                continue
            papers.append(
                PaperDocument(
                    paper_id=item.get("paperId", item["title"][:32]),
                    title=item["title"],
                    abstract=abstract,
                    year=int(item.get("year") or 0),
                    authors=[author.get("name", "") for author in item.get("authors", []) if author.get("name")],
                    topics=[field for field in item.get("fieldsOfStudy", []) if field],
                )
            )
        return papers

    def _get_json(self, url: str, headers: dict[str, str]) -> dict:
        request = urllib.request.Request(url, headers=headers, method="GET")
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except ssl.SSLCertVerificationError:
            insecure_context = ssl._create_unverified_context()
            with urllib.request.urlopen(request, timeout=20, context=insecure_context) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            if "CERTIFICATE_VERIFY_FAILED" in str(exc):
                insecure_context = ssl._create_unverified_context()
                with urllib.request.urlopen(request, timeout=20, context=insecure_context) as response:
                    return json.loads(response.read().decode("utf-8"))
            raise LiteratureFetchError(f"Semantic Scholar request failed: {exc}") from exc


class ArxivFetcher:
    BASE_URL = "http://export.arxiv.org/api/query"
    XML_NS = {"atom": "http://www.w3.org/2005/Atom"}

    def search(self, query: str, limit: int = 5) -> list[PaperDocument]:
        params = {
            "search_query": f"all:{query}",
            "start": "0",
            "max_results": str(limit),
        }
        url = f"{self.BASE_URL}?{urllib.parse.urlencode(params)}"
        request = urllib.request.Request(url, headers={"User-Agent": "AI-Scientist/0.1"}, method="GET")

        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                xml_payload = response.read().decode("utf-8")
        except ssl.SSLCertVerificationError:
            insecure_context = ssl._create_unverified_context()
            with urllib.request.urlopen(request, timeout=20, context=insecure_context) as response:
                xml_payload = response.read().decode("utf-8")
        except Exception as exc:
            if "CERTIFICATE_VERIFY_FAILED" in str(exc):
                insecure_context = ssl._create_unverified_context()
                with urllib.request.urlopen(request, timeout=20, context=insecure_context) as response:
                    xml_payload = response.read().decode("utf-8")
            else:
                raise LiteratureFetchError(f"arXiv request failed: {exc}") from exc

        root = ET.fromstring(xml_payload)
        papers: list[PaperDocument] = []
        for entry in root.findall("atom:entry", self.XML_NS):
            title = normalize_text(entry.findtext("atom:title", default="", namespaces=self.XML_NS))
            abstract = normalize_text(entry.findtext("atom:summary", default="", namespaces=self.XML_NS))
            published = entry.findtext("atom:published", default="", namespaces=self.XML_NS)
            authors = [
                normalize_text(author.findtext("atom:name", default="", namespaces=self.XML_NS))
                for author in entry.findall("atom:author", self.XML_NS)
            ]
            identifier = normalize_text(entry.findtext("atom:id", default="", namespaces=self.XML_NS))
            if not title or not abstract:
                continue
            papers.append(
                PaperDocument(
                    paper_id=identifier or title[:32],
                    title=title,
                    abstract=abstract,
                    year=int(published[:4]) if published[:4].isdigit() else 0,
                    authors=[author for author in authors if author],
                    topics=["arxiv"],
                )
            )
        return papers


class LiteratureCollectionService:
    def __init__(
        self,
        semantic_scholar: SemanticScholarFetcher | None = None,
        arxiv: ArxivFetcher | None = None,
    ):
        self.semantic_scholar = semantic_scholar or SemanticScholarFetcher()
        self.arxiv = arxiv or ArxivFetcher()

    def collect(self, query: str, limit_per_source: int = 5) -> list[PaperDocument]:
        combined: list[PaperDocument] = []
        seen_titles: set[str] = set()
        errors: list[str] = []

        for fetcher in (self.semantic_scholar, self.arxiv):
            try:
                papers = fetcher.search(query=query, limit=limit_per_source)
            except LiteratureFetchError as exc:
                errors.append(str(exc))
                continue
            for paper in papers:
                key = paper.title.lower()
                if key in seen_titles:
                    continue
                combined.append(paper)
                seen_titles.add(key)
        if not combined and errors:
            raise LiteratureFetchError("; ".join(errors))
        return combined

    def export(self, papers: list[PaperDocument], output_path: str | Path) -> None:
        payload = {"papers": [asdict(paper) for paper in papers]}
        Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
