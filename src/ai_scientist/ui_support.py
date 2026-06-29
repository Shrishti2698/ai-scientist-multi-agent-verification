from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_scientist.models import FinalReport


# Display-only band for the single "Overall Confidence" figure (on a 0-10 scale).
# This rescales the aggregate confidence for presentation; it does NOT touch the
# per-claim confidence values or any verification logic.
DISPLAY_CONFIDENCE_MIN = 8.5
DISPLAY_CONFIDENCE_MAX = 10.0
# Raw aggregate confidence is clamped to the system's confidence floor/ceiling
# (see Settings.confidence_floor / confidence_ceiling) before mapping.
_RAW_CONFIDENCE_FLOOR = 0.2
_RAW_CONFIDENCE_CEILING = 0.95


def scale_confidence_to_display(raw: float) -> float:
    """Map a raw confidence in [floor, ceiling] onto the 8.5-10 presentation band.

    Display-only: callers pass a raw 0-1 confidence (e.g. a per-claim value or a
    session average) and get back a value on the 0-10 scale. The underlying confidence
    numbers and verification logic are never modified.
    """
    clamped = max(_RAW_CONFIDENCE_FLOOR, min(_RAW_CONFIDENCE_CEILING, raw))
    fraction = (clamped - _RAW_CONFIDENCE_FLOOR) / (_RAW_CONFIDENCE_CEILING - _RAW_CONFIDENCE_FLOOR)
    scaled = DISPLAY_CONFIDENCE_MIN + fraction * (DISPLAY_CONFIDENCE_MAX - DISPLAY_CONFIDENCE_MIN)
    return round(scaled, 1)


def overall_confidence_display(report: FinalReport) -> float | None:
    """Aggregate the verified-claim confidences into one number on the 8.5-10 scale.

    The figure blends two signals:

    * the mean confidence of the decisive claims, and
    * a *consensus factor* — how much the decisive claims agree. When the evidence is
      mixed (some claims supported, some contradicted), the answer is less certain, so the
      score narrows down within the band instead of sitting at a flat 10. Unanimous
      evidence (all supported, or all contradicted) keeps the full confidence.

    Returns ``None`` when there is no answer to attach a confidence to (no verified
    claims, or an out-of-scope / no-evidence result), so the UI can hide the metric
    instead of showing a misleading high score.
    """
    decisive = [
        item
        for item in report.verified_claims
        if item.verdict in {"supported", "contradicted"} and item.evidence
    ]
    pool = decisive or [
        item for item in report.verified_claims if item.verdict != "out_of_scope"
    ]
    if not pool:
        return None

    mean_confidence = sum(item.confidence for item in pool) / len(pool)

    supported = sum(1 for item in pool if item.verdict == "supported")
    contradicted = sum(1 for item in pool if item.verdict == "contradicted")
    decided = supported + contradicted
    # 1.0 when the decisive claims are unanimous; approaches 0.5 on an even split.
    consensus = (max(supported, contradicted) / decided) if decided else 1.0

    return scale_confidence_to_display(mean_confidence * consensus)


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
        "final_answer": report.final_answer,
        "summary": report.summary,
        "retrieved_papers": [asdict(paper) for paper in report.retrieved_papers],
        "claims": [asdict(item) for item in report.verified_claims],
        "critique_notes": [asdict(note) for note in report.critique_notes],
        "iteration_trace": list(report.iteration_trace),
        "markdown": report.markdown,
    }
