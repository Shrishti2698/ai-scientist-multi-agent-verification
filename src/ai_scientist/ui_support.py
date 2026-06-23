from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_scientist.models import FinalReport


def available_corpus_options(root: str | Path) -> dict[str, Path]:
    base = Path(root)
    options = {
        "Final Demo Corpus": base / "data" / "final_demo_corpus.json",
        "Sample Corpus": base / "data" / "sample_corpus.json",
    }
    live_path = base / "data" / "live_corpus.json"
    if live_path.exists():
        options["Live Corpus Snapshot"] = live_path
    return options


def report_to_sections(report: FinalReport) -> dict[str, object]:
    return {
        "question": report.question,
        "summary": report.summary,
        "retrieved_papers": [asdict(paper) for paper in report.retrieved_papers],
        "claims": [asdict(item) for item in report.verified_claims],
        "critique_notes": [asdict(note) for note in report.critique_notes],
        "iteration_trace": list(report.iteration_trace),
        "markdown": report.markdown,
    }
