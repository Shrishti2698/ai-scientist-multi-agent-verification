"""Generate ready-to-upload REAL paper files for the demo.

For each demo domain (matching the queries in AI_Scientist_Project_Proposal),
this fetches 3-4 genuinely relevant papers from arXiv / PubMed and writes one
JSON file per paper into demo_uploads/<domain>/. It also writes
demo_uploads/README.md mapping each demo query to the files to upload and the
real source link for every paper.

Nothing is hardcoded or faked: abstracts are the real ones returned by the APIs.
The papers are simply pre-selected so that, when uploaded, they match the demo
queries and legitimately drive up the uploaded-paper count and confidence.

Run:  $env:PYTHONPATH='src'; python scripts/build_demo_uploads.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ai_scientist.bootstrap import load_environment
from ai_scientist.config import Settings
from ai_scientist.agents.live_retrieval import LiveRetrievalAgent
from ai_scientist.utils import coverage_score

load_environment()

ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = ROOT / "demo_uploads"

# domain -> (display, demo queries, search source, search queries, topic tags, target count)
DOMAINS = {
    "medicine": {
        "display": "🩺 Medicine",
        "demo_queries": [
            "Does metformin show better weight management outcomes than insulin in diabetes treatment?",
            "Do metformin patients experience fewer hypoglycemic episodes compared to insulin patients?",
            "Is telemedicine effective for rural healthcare delivery?",
        ],
        "source": "pubmed",
        "search_queries": [
            "metformin versus insulin type 2 diabetes weight glycemic control",
            "metformin insulin hypoglycemia type 2 diabetes",
            "telemedicine rural healthcare access outcomes",
        ],
        "topics": ["diabetes", "metformin", "insulin", "treatment", "telemedicine", "weight", "hypoglycemia"],
        "count": 4,
    },
    "ai_cs": {
        "display": "🤖 AI / Computer Science",
        "demo_queries": [
            "Do critic-guided verification loops improve research claim checking?",
            "Does retrieval-augmented generation reduce hallucination in language models?",
            "Do multi-agent systems improve evidence coverage compared to single-agent baselines?",
        ],
        "source": "arxiv",
        "search_queries": [
            "retrieval augmented generation reduce hallucination language models",
            "multi-agent verification critique language models factuality",
            "self verification critic feedback reduce hallucination LLM",
        ],
        "topics": ["rag", "hallucination", "language models", "multi-agent", "verification", "critic", "evidence"],
        "count": 4,
    },
    "biology": {
        "display": "🧬 Biology",
        "demo_queries": [
            "Is CRISPR-Cas9 effective for treating sickle cell disease?",
            "Does CRISPR gene therapy reduce pain crisis frequency in sickle cell patients?",
            "Do CRISPR treatments show improvement in hemoglobin levels?",
        ],
        "source": "pubmed",
        "search_queries": [
            "CRISPR Cas9 sickle cell disease gene therapy",
            "CRISPR gene editing sickle cell hemoglobin fetal",
            "gene therapy sickle cell disease clinical outcomes",
        ],
        "topics": ["crispr", "gene therapy", "sickle cell", "hemoglobin", "gene editing"],
        "count": 4,
    },
    "psychology": {
        "display": "🧠 Psychology",
        "demo_queries": [
            "Does social media usage increase depression in adolescents?",
            "Do brain training apps improve working memory in older adults?",
            "Is passive social media consumption more harmful than active engagement?",
        ],
        "source": "pubmed",
        "search_queries": [
            "social media use depression adolescents longitudinal",
            "cognitive brain training working memory older adults randomized",
            "passive active social media use wellbeing affect",
        ],
        "topics": ["social media", "depression", "adolescents", "brain training", "working memory", "older adults"],
        "count": 4,
    },
}

MIN_ABSTRACT = 250
MIN_RELEVANCE = 0.40


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", text.lower()).strip("_")[:40]


def source_url(paper_id: str) -> str:
    if paper_id.startswith("ARXIV_"):
        return f"https://arxiv.org/abs/{paper_id[len('ARXIV_'):]}"
    if paper_id.startswith("PMC_"):
        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{paper_id[len('PMC_'):]}/"
    return ""


agent = LiveRetrievalAgent(Settings())
index_lines = [
    "# Demo Upload Pack — real papers, ready to drag into the UI",
    "",
    "Each folder holds 3-4 **real** paper files (JSON, fetched from arXiv/PubMed).",
    "For any demo query in a domain, upload **all the files in that domain folder** in the",
    "Streamlit sidebar, then ask the query. Uploaded papers outrank the corpus and live APIs,",
    "so the 📤 Uploaded count and confidence climb — while live retrieval still adds 🌐 papers.",
    "",
]

OUT_DIR.mkdir(exist_ok=True)

for domain_key, cfg in DOMAINS.items():
    domain_dir = OUT_DIR / domain_key
    domain_dir.mkdir(exist_ok=True)
    print(f"\n=== {cfg['display']} ===", flush=True)

    collected: list[tuple] = []  # (paper, best_relevance)
    seen_titles: list[str] = []

    for sq in cfg["search_queries"]:
        if len(collected) >= cfg["count"]:
            break
        try:
            if cfg["source"] == "arxiv":
                fetched = agent._retrieve_from_arxiv(sq, max_results=6)
            else:
                fetched = agent._retrieve_from_pubmed(sq, max_results=6)
        except Exception as exc:  # pragma: no cover
            print(f"   fetch failed for {sq!r}: {exc}")
            continue

        for p in fetched:
            if len(collected) >= cfg["count"]:
                break
            if len(p.abstract) < MIN_ABSTRACT or "not available" in p.abstract.lower():
                continue
            # relevance against the closest demo query
            rel = max(coverage_score(q, f"{p.title} {p.abstract}") for q in cfg["demo_queries"])
            if rel < MIN_RELEVANCE:
                continue
            if any(coverage_score(p.title, t) > 0.6 for t in seen_titles):
                continue  # near-duplicate title
            seen_titles.append(p.title)
            collected.append((p, rel))

    if not collected:
        print("   WARNING: no papers collected")
    files_for_index = []
    for i, (p, rel) in enumerate(collected, start=1):
        upload_id = f"UP_{domain_key.upper()}_{i:02d}"
        record = {
            "paper_id": upload_id,
            "title": p.title,
            "abstract": p.abstract,
            "year": p.year,
            "authors": p.authors,
            "topics": cfg["topics"],
            "source_url": source_url(p.paper_id),
        }
        fname = f"{i:02d}_{slug(p.title)}.json"
        (domain_dir / fname).write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
        files_for_index.append((fname, p.title, record["source_url"]))
        print(f"   + {fname}  (rel={rel:.2f})  {p.title[:55]}")

    # index section
    index_lines.append(f"## {cfg['display']}  (`demo_uploads/{domain_key}/`)")
    index_lines.append("")
    index_lines.append("**Ask any of:**")
    for q in cfg["demo_queries"]:
        index_lines.append(f"- {q}")
    index_lines.append("")
    index_lines.append("**Upload these files:**")
    for fname, title, url in files_for_index:
        link = f" — [source]({url})" if url else ""
        index_lines.append(f"- `{fname}` — {title}{link}")
    index_lines.append("")

(OUT_DIR / "README.md").write_text("\n".join(index_lines), encoding="utf-8")
print(f"\nWrote demo files + index under {OUT_DIR}")
