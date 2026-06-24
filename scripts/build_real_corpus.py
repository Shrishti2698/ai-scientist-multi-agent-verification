"""Build an offline demo corpus from REAL papers fetched via arXiv / PubMed.

This replaces the previous synthetic (self-corroborating) abstracts with genuine
abstracts so high-confidence results are legitimate. Run:

    $env:PYTHONPATH='src'; python scripts/build_real_corpus.py

It writes data/all_domains_corpus.json. The unit-test fixtures
(sample_corpus.json, final_demo_corpus.json) are intentionally left untouched.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_scientist.bootstrap import load_environment
from ai_scientist.config import Settings
from ai_scientist.agents.live_retrieval import LiveRetrievalAgent
from ai_scientist.utils import coverage_score

load_environment()

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "all_domains_corpus.json"

# (clean id prefix, source, query, how many to keep, topics)
PLAN = [
    ("AI", "arxiv", "retrieval augmented generation reduce hallucination factual grounding", 2, ["rag", "hallucination", "language models"]),
    ("AI", "arxiv", "multi-agent debate improve factuality reasoning language models", 1, ["multi-agent", "reasoning", "verification"]),
    ("PHY", "arxiv", "quantum error correction surface code fault tolerant", 2, ["quantum computing", "error correction"]),
    ("ENV", "arxiv", "solar photovoltaic wind energy efficiency comparison", 1, ["renewable energy", "solar", "wind"]),
    ("ECON", "arxiv", "remote work productivity firms evidence", 1, ["remote work", "productivity", "economics"]),
    ("MED", "pubmed", "metformin insulin type 2 diabetes glycemic control", 2, ["diabetes", "metformin", "treatment"]),
    ("MED", "pubmed", "telemedicine rural healthcare access outcomes", 1, ["telemedicine", "healthcare access"]),
    ("BIO", "pubmed", "CRISPR Cas9 sickle cell disease gene therapy", 1, ["crispr", "gene therapy", "sickle cell"]),
    ("PSY", "pubmed", "social media use depression adolescents longitudinal", 1, ["social media", "depression", "adolescents"]),
    ("NEURO", "pubmed", "cognitive training brain training older adults randomized", 1, ["cognitive training", "older adults"]),
    ("CHEM", "pubmed", "green chemistry pharmaceutical solvent sustainable synthesis", 1, ["green chemistry", "pharmaceuticals"]),
    ("EDU", "pubmed", "online learning student performance outcomes education", 1, ["online learning", "education"]),
]

MIN_ABSTRACT = 250

agent = LiveRetrievalAgent(Settings())
papers: list[dict] = []
counters: dict[str, int] = {}


def clean_id(prefix: str) -> str:
    counters[prefix] = counters.get(prefix, 0) + 1
    return f"{prefix}{counters[prefix]:03d}"


for prefix, source, query, keep, topics in PLAN:
    print(f"[{source}] {query!r} ...", flush=True)
    try:
        if source == "arxiv":
            fetched = agent._retrieve_from_arxiv(query, max_results=keep + 4)
        else:
            fetched = agent._retrieve_from_pubmed(query, max_results=keep + 4)
    except Exception as exc:  # pragma: no cover
        print(f"   FAILED: {exc}")
        continue

    added = 0
    for p in fetched:
        if added >= keep:
            break
        if len(p.abstract) < MIN_ABSTRACT or "not available" in p.abstract.lower():
            continue
        # Reject papers that don't actually match the query topic (PubMed/arXiv
        # sometimes returns loosely-related results).
        relevance = coverage_score(query, f"{p.title} {p.abstract}")
        if relevance < 0.45:
            print(f"   - skip (relevance {relevance:.2f}): {p.title[:55]}")
            continue
        papers.append({
            "paper_id": clean_id(prefix),
            "title": p.title,
            "abstract": p.abstract,
            "year": p.year,
            "authors": p.authors,
            "topics": topics,
        })
        added += 1
        print(f"   + {papers[-1]['paper_id']} | {p.title[:60]} | abs={len(p.abstract)}")

print(f"\nCollected {len(papers)} real papers.")
OUT.write_text(json.dumps({"papers": papers}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote {OUT}")
