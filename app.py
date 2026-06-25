from __future__ import annotations

import hashlib
import os
import time
from dataclasses import asdict
from pathlib import Path

try:
    import streamlit as st
except ModuleNotFoundError:
    st = None

from ai_scientist.bootstrap import load_environment
from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.baselines import RagBaseline, SingleAgentBaseline
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.ingestion import IngestionError, RawPaperIngestor
from ai_scientist.accuracy import AccuracyCalculator


ROOT = Path(__file__).resolve().parent
DEFAULT_CORPUS = ROOT / "data" / "all_domains_corpus.json"
SAMPLE_CORPUS = ROOT / "data" / "sample_corpus.json"

# (model_id, short label, approx cost PER LLM CALL). Costs are rough estimates for a
# typical verification/summary call (~1-2k tokens); a full analysis makes several calls.
MODEL_OPTIONS = [
    ("gpt-5.5", "GPT-5.5 — most capable", "~$0.03/call"),
    ("gpt-5.4", "GPT-5.4 — strong reasoning", "~$0.02/call"),
    ("gpt-5.4-mini", "GPT-5.4-mini — fast & cheap", "~$0.004/call"),
    ("gpt-4o", "GPT-4o — balanced (no reasoning)", "~$0.008/call"),
    ("gpt-4o-mini", "GPT-4o-mini — cheapest", "~$0.0005/call"),
]
INGESTOR = RawPaperIngestor()

load_environment()


def build_active_corpus(corpus_path: Path, uploaded_files=None):
    # Start from the curated base corpus, then merge any uploaded papers into it.
    base_papers = CorpusRepository.from_path(corpus_path).all_papers()
    uploaded_papers = []
    upload_errors: list[str] = []

    for uploaded_file in uploaded_files or []:
        try:
            uploaded_papers.extend(INGESTOR.ingest_uploaded(uploaded_file.name, uploaded_file.getvalue()))
        except IngestionError as exc:
            upload_errors.append(f"{uploaded_file.name}: {exc}")

    active_corpus = CorpusRepository(base_papers + uploaded_papers)
    return active_corpus, uploaded_papers, upload_errors


def compute_corpus_signature(corpus_path: Path, uploaded_files=None) -> str:
    digest = hashlib.sha256(str(corpus_path).encode("utf-8"))
    for uploaded_file in uploaded_files or []:
        digest.update(uploaded_file.name.encode("utf-8"))
        digest.update(uploaded_file.getvalue())
    return digest.hexdigest()


def load_systems(corpus_path: Path, uploaded_files=None, use_llm: bool = False, model: str | None = None):
    corpus, uploaded_papers, upload_errors = build_active_corpus(corpus_path, uploaded_files)
    # Hybrid demo: LLM when a key is present, plus live API augmentation on top of the corpus.
    # A wider retrieval window so uploaded papers AND live-API papers both surface
    # (with the default top_k=3, a handful of uploads would crowd out every API result).
    overrides = {
        "enable_openai_llm": use_llm,
        "enable_live_retrieval": True,
        "top_k_retrieval": 8,
        "second_pass_top_k": 8,
    }
    if model:
        overrides["openai_model"] = model
    settings = Settings.from_env(**overrides)
    
    system = MultiAgentResearchSystem(settings=settings, corpus=corpus)
    # Pass uploaded papers to the hybrid retrieval system
    system.add_uploaded_papers(uploaded_papers)
    
    return (
        system,
        SingleAgentBaseline(settings=settings, corpus=corpus),
        RagBaseline(settings=settings, corpus=corpus),
        corpus,
        uploaded_papers,
        upload_errors,
    )


def get_paper_source_info(paper, uploaded_papers, corpus_ids=None):
    """Determine the source of a paper: uploaded, live API, or curated corpus."""
    uploaded_ids = {p.paper_id for p in uploaded_papers}
    corpus_ids = corpus_ids or set()

    if paper.paper_id in uploaded_ids:
        return "uploaded", "📤 Uploaded", "#f0fff0"
    elif paper.paper_id.startswith("PMC_"):
        return "api_pubmed", "🏥 PubMed (live)", "#e8f5e8"
    elif paper.paper_id.startswith("ARXIV_"):
        return "api_arxiv", "🔬 arXiv (live)", "#e8f4f8"
    elif paper.paper_id in corpus_ids:
        return "corpus", "📚 Curated Corpus", "#eef2ff"
    else:
        # Fallback for any paper whose source we can't classify.
        return "unknown", "❓ Unknown", "#f8f8f8"


def render_paper_source_badge(source_type, source_label, bg_color, paper_title):
    """Render a paper with source-colored badge."""
    return f"""
    <div style="background-color: {bg_color}; padding: 8px; border-radius: 5px; margin: 2px 0;">
        <strong style="color: #000000;">{source_label}</strong> 
        <span style="font-family: monospace; color: #000000;">{paper_title}</span>
    </div>
    """


def render_claim_card(item, uploaded_papers=None, corpus_ids=None) -> None:
    uploaded_papers = uploaded_papers or []
    corpus_ids = corpus_ids or set()

    with st.container(border=True):
        # Determine claim source type
        claim_source_type, claim_source_label, claim_bg_color = get_paper_source_info(
            type('obj', (object,), {'paper_id': item.claim.source_paper_id})(),
            uploaded_papers, corpus_ids
        )
        
        st.subheader(item.claim.text)
        
        # Show claim source with colored badge
        st.markdown(
            render_paper_source_badge(
                claim_source_type, claim_source_label, claim_bg_color, 
                f"Claim from: {item.claim.source_title}"
            ), 
            unsafe_allow_html=True
        )
        
        left, right = st.columns(2)
        left.metric("Verdict", item.verdict)
        right.metric("Confidence", f"{item.confidence:.3f}")
        st.caption(
            f"Type: {item.claim.claim_type} | Focus: {', '.join(item.claim.focus_terms) if item.claim.focus_terms else 'None'}"
        )
        st.write(item.rationale)

        if item.evidence:
            supporting = [e for e in item.evidence if item.verdict != "contradicted"]
            contradicting = [e for e in item.evidence if item.verdict == "contradicted"]

            if supporting:
                st.markdown("**Supporting Evidence** (papers that back this claim)")
                for snippet in supporting:
                    # Determine evidence source
                    evidence_source_type, evidence_source_label, evidence_bg_color = get_paper_source_info(
                        type('obj', (object,), {'paper_id': snippet.paper_id})(),
                        uploaded_papers, corpus_ids
                    )
                    
                    st.markdown(
                        render_paper_source_badge(
                            evidence_source_type, evidence_source_label, evidence_bg_color,
                            f"{snippet.title} (overlap={snippet.overlap_score})"
                        ),
                        unsafe_allow_html=True
                    )
                    st.success(f"> {snippet.sentence}")

            if contradicting:
                st.markdown("**Contradicting / Verification Sources**")
                for snippet in contradicting:
                    # Determine evidence source
                    evidence_source_type, evidence_source_label, evidence_bg_color = get_paper_source_info(
                        type('obj', (object,), {'paper_id': snippet.paper_id})(),
                        uploaded_papers, corpus_ids
                    )
                    
                    st.markdown(
                        render_paper_source_badge(
                            evidence_source_type, evidence_source_label, "#ffe8e8",  # Red tint for contradicting
                            f"{snippet.title} (overlap={snippet.overlap_score})"
                        ),
                        unsafe_allow_html=True
                    )
                    st.error(f"> {snippet.sentence}")
        else:
            st.write("No evidence snippets available.")


def _trace_icon(step: str) -> str:
    lowered = step.lower()
    if "pass 2" in lowered or "re-verif" in lowered or "revisited" in lowered:
        return "🔁"
    if "retriev" in lowered or "pass 1" in lowered:
        return "🔍"
    if "claim" in lowered:
        return "🧩"
    if "critic" in lowered:
        return "🧐"
    if "scope" in lowered or "stopped" in lowered:
        return "🛑"
    return "▫️"


def render_orchestration_trace(report) -> None:
    """Render the step-by-step agent pipeline so the reasoning path is obvious."""
    with st.expander("🛰️ Orchestration Trace — how the agents reached this answer", expanded=True):
        st.caption(
            "Agent pipeline:  🔍 Retrieval → 🧩 Claim Extraction → ✅ Verification → "
            "🧐 Critic → 🔁 Targeted Re-verification → 📝 Synthesis"
        )
        st.markdown("**Step-by-step trace**")
        for index, step in enumerate(report.iteration_trace, start=1):
            icon = _trace_icon(step)
            highlight = icon == "🔁"
            text = f"**{index}.** {icon} {step}"
            if highlight:
                st.markdown(f"> {text}")  # visually offset the critic-triggered second pass
            else:
                st.markdown(text)
        if not report.iteration_trace:
            st.write("No trace steps were recorded for this run.")


def main() -> None:
    if st is None:
        raise SystemExit(
            "Streamlit is not installed. Install dependencies, then run: streamlit run app.py"
        )

    st.set_page_config(
        page_title="AI-Scientist Demo",
        page_icon=":microscope:",
        layout="wide",
    )

    st.title("AI-Scientist")
    st.caption(
        "Interactive multi-agent research verification system. Upload papers from any research domain "
        "or leverage live retrieval from PubMed, arXiv, and other research databases."
    )

    # Session-scoped accuracy tracker so the metrics reflect THIS session, not every
    # query the server has ever processed.
    if "accuracy_tracker" not in st.session_state:
        st.session_state["accuracy_tracker"] = AccuracyCalculator()
    accuracy_tracker = st.session_state["accuracy_tracker"]

    with st.sidebar:
        st.header("Demo Setup")
        corpus_choice = st.info("📚 **Multi-domain Research System**: Hybrid approach combining uploaded papers + live API retrieval")
        llm_available = bool(os.getenv("OPENAI_API_KEY"))
        model_choice = st.selectbox(
            "LLM model",
            MODEL_OPTIONS,
            format_func=lambda option: f"{option[1]}  ({option[2]})",
            disabled=not llm_available,
            help="Model used for claim verification and the summary. Costs are approximate per LLM call.",
        )
        if llm_available:
            st.caption(f"Using **{model_choice[0]}** · approx **{model_choice[2]}**")
        else:
            st.caption("Set OPENAI_API_KEY in .env to enable LLM mode (currently heuristic).")
        uploaded_files = st.file_uploader(
            "Upload paper(s)",
            type=["md", "txt", "json", "pdf"],
            accept_multiple_files=True,
            help="Upload your own paper to add it to the active corpus for this session.",
        )
        question = st.text_area(
            "Research question",
            value="Do critic-guided verification loops improve research claim checking?",
            height=120,
        )
        run_clicked = st.button("Run Analysis", type="primary", use_container_width=True)
        st.divider()
        st.write("Use the frozen corpus during thesis demos for maximum reliability.")
        if uploaded_files:
            st.success(f"{len(uploaded_files)} file(s) ready to merge into the corpus.")

    corpus_path = Path(str(DEFAULT_CORPUS))  # Use default since no dropdown
    selected_model = model_choice[0]
    corpus_signature = f"{compute_corpus_signature(corpus_path, uploaded_files)}::{selected_model}"
    system, single_agent, rag, corpus, uploaded_papers, upload_errors = load_systems(
        corpus_path,
        uploaded_files,
        use_llm=llm_available,
        model=selected_model,
    )

    for message in upload_errors:
        st.sidebar.error(message)

    if run_clicked or st.session_state.get("last_run_signature") != corpus_signature:
        start_time = time.time()
        report = system.analyze_question(question)
        response_time = time.time() - start_time
        
        # Track accuracy metrics
        accuracy_tracker.log_query_performance(question, report, response_time)
        
        st.session_state["last_report"] = report
        st.session_state["baseline_single"] = single_agent.verify_claim(question)
        st.session_state["baseline_rag"] = rag.verify_claim(question)
        st.session_state["last_run_signature"] = corpus_signature
    else:
        report = st.session_state["last_report"]

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Multi-Agent Report")
        if not report.verified_claims and "research question" in report.summary:
            st.warning(report.summary)
        st.write(report.summary)

        corpus_ids = {paper.paper_id for paper in corpus.all_papers()}
        uploaded_ids = {up.paper_id for up in uploaded_papers}

        # Classify every retrieved paper by source (priority: uploaded > API > corpus).
        uploaded_retrieved = [p for p in report.retrieved_papers if p.paper_id in uploaded_ids]
        api_retrieved = [p for p in report.retrieved_papers if p.paper_id.startswith(("PMC_", "ARXIV_"))]
        corpus_retrieved = [
            p for p in report.retrieved_papers
            if p.paper_id not in uploaded_ids
            and not p.paper_id.startswith(("PMC_", "ARXIV_"))
        ]

        metrics = st.columns(3)
        metrics[0].metric("Claims Verified", len(report.verified_claims), help="Research claims extracted from the retrieved papers and individually verified")
        metrics[1].metric("Papers Retrieved", len(report.retrieved_papers), help="Total papers grounding this analysis (uploaded + curated corpus + live APIs)")
        metrics[2].metric("Critique Issues", len(report.critique_notes), help="Distinct issue categories flagged by the Critic Agent")

        render_orchestration_trace(report)

        with st.expander(f"Retrieved Papers ({len(report.retrieved_papers)})", expanded=False):
            st.caption("Every paper that grounded this analysis, grouped by where it came from.")

            if uploaded_retrieved:
                st.markdown("**📤 From your uploads** (highest priority)")
                for paper in uploaded_retrieved:
                    st.success(f"✅ **{paper.title}** ({paper.year}) — {', '.join(paper.authors)}")

            if corpus_retrieved:
                st.markdown("**📚 From the curated corpus**")
                for paper in corpus_retrieved:
                    st.markdown(f"📚 **{paper.title}** ({paper.year}) — {', '.join(paper.authors)}")

            if api_retrieved:
                st.markdown("**🌐 From live research databases**")
                for paper in api_retrieved:
                    source = "🏥 PubMed" if paper.paper_id.startswith("PMC_") else "🔬 arXiv"
                    st.markdown(f"{source}: **{paper.title}** ({paper.year}) — {', '.join(paper.authors)}")

            if not report.retrieved_papers:
                st.write("No papers were retrieved for this query.")

        # Optional section for uploaded papers (only show if papers were uploaded)
        if uploaded_papers:
            with st.expander(f"📤 Uploaded Papers ({len(uploaded_papers)} total)", expanded=False):
                st.caption("Papers uploaded this session (used only when relevant to the query)")
                for paper in uploaded_papers:
                    used_icon = "✅ Used" if paper.paper_id in {p.paper_id for p in report.retrieved_papers} else "⚪ Available"
                    st.write(f"- {used_icon} **{paper.title}** ({paper.year}) | {', '.join(paper.authors)}")

        # Source breakdown summary
        if report.retrieved_papers:
            with st.container():
                st.markdown("#### 📊 Source Analysis Summary")
                source_cols = st.columns(3)
                source_cols[0].metric("📤 Uploaded", len(uploaded_retrieved), help="Your uploaded papers used (preferred over all other sources)")
                source_cols[1].metric("📚 Curated Corpus", len(corpus_retrieved), help="Papers from the built-in offline corpus")
                source_cols[2].metric("🌐 Live APIs", len(api_retrieved), help="Papers fetched live from PubMed / arXiv")

                parts = []
                if uploaded_retrieved:
                    parts.append(f"{len(uploaded_retrieved)} uploaded")
                if corpus_retrieved:
                    parts.append(f"{len(corpus_retrieved)} from the curated corpus")
                if api_retrieved:
                    parts.append(f"{len(api_retrieved)} from live databases")
                st.info("Grounded on " + ", ".join(parts) + ".")

        st.subheader("Verified Claims")

        for item in report.verified_claims:
            render_claim_card(item, uploaded_papers, corpus_ids)

    with right:
        st.subheader("Baseline Snapshot")
        single = st.session_state["baseline_single"]
        rag_result = st.session_state["baseline_rag"]

        with st.container(border=True):
            st.markdown("**Single-Agent Baseline**")
            st.write(f"Verdict: `{single.verdict}`")
            st.write(f"Confidence: `{single.confidence:.3f}`")
            st.caption(single.rationale)

        with st.container(border=True):
            st.markdown("**RAG Baseline**")
            st.write(f"Verdict: `{rag_result.verdict}`")
            st.write(f"Confidence: `{rag_result.confidence:.3f}`")
            st.caption(rag_result.rationale)

        with st.container(border=True):
            st.markdown("**System Accuracy Metrics**")
            accuracy_summary = accuracy_tracker.get_accuracy_summary()
            if accuracy_summary:
                acc_cols = st.columns(2)
                acc_cols[0].metric(
                    "Retrieval Success", 
                    f"{accuracy_summary['retrieval_success_rate']:.1%}",
                    help="Percentage of queries that found relevant papers"
                )
                acc_cols[1].metric(
                    "Claim Extraction", 
                    f"{accuracy_summary['claim_extraction_rate']:.1%}",
                    help="Percentage of queries that extracted verifiable claims"
                )
                st.metric(
                    "Avg Confidence", 
                    f"{accuracy_summary['average_confidence']:.3f}",
                    help="Average confidence score across recent analyses"
                )
                st.metric(
                    "Response Time", 
                    f"{accuracy_summary['average_response_time']:.2f}s",
                    help="Average time to complete analysis"
                )
            else:
                st.write("No performance data available yet. Run some analyses to see metrics.")

        with st.container(border=True):
            st.markdown("**Critique Notes**")
            if report.critique_notes:
                severity_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                for note in report.critique_notes:
                    icon = severity_colors.get(note.severity, "ℹ️")
                    st.warning(f"{icon} **{note.severity.upper()}**: {note.message}")
            else:
                st.write("No critique issues identified in this pass.")

        with st.expander("Structured JSON View", expanded=False):
            st.json(
                {
                    "question": report.question,
                    "summary": report.summary,
                    "retrieved_papers": [asdict(paper) for paper in report.retrieved_papers],
                    "verified_claims": [asdict(item) for item in report.verified_claims],
                    "critique_notes": [asdict(item) for item in report.critique_notes],
                    "iteration_trace": report.iteration_trace,
                }
            )


if __name__ == "__main__":
    main()
