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
DEFAULT_CORPUS = ROOT / "data" / "final_demo_corpus.json"
SAMPLE_CORPUS = ROOT / "data" / "sample_corpus.json"
INGESTOR = RawPaperIngestor()
ACCURACY_TRACKER = AccuracyCalculator()

load_environment()


def build_active_corpus(corpus_path: Path, uploaded_files=None):
    # Only process uploaded files, no base corpus
    uploaded_papers = []
    upload_errors: list[str] = []

    for uploaded_file in uploaded_files or []:
        try:
            uploaded_papers.extend(INGESTOR.ingest_uploaded(uploaded_file.name, uploaded_file.getvalue()))
        except IngestionError as exc:
            upload_errors.append(f"{uploaded_file.name}: {exc}")

    # Create empty corpus for API-only system
    empty_corpus = CorpusRepository([])
    return empty_corpus, uploaded_papers, upload_errors


def compute_corpus_signature(corpus_path: Path, uploaded_files=None) -> str:
    digest = hashlib.sha256(str(corpus_path).encode("utf-8"))
    for uploaded_file in uploaded_files or []:
        digest.update(uploaded_file.name.encode("utf-8"))
        digest.update(uploaded_file.getvalue())
    return digest.hexdigest()


def load_systems(corpus_path: Path, uploaded_files=None, use_llm: bool = False):
    corpus, uploaded_papers, upload_errors = build_active_corpus(corpus_path, uploaded_files)
    settings = Settings(enable_openai_llm=use_llm, enable_live_retrieval=True)  # Always enable live retrieval for hybrid
    
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


def get_paper_source_info(paper, uploaded_papers, base_corpus_papers=None):
    """Determine detailed source information for a paper - only uploaded or API."""
    uploaded_ids = {p.paper_id for p in uploaded_papers}
    
    if paper.paper_id.startswith("PMC_"):
        return "api_pubmed", "🏥 PubMed", "#e8f5e8"
    elif paper.paper_id.startswith("ARXIV_"):
        return "api_arxiv", "🔬 arXiv", "#e8f4f8"
    elif paper.paper_id in uploaded_ids:
        return "uploaded", "📤 Uploaded", "#f0fff0"
    else:
        # Fallback for any other papers (shouldn't happen in hybrid mode)
        return "unknown", "❓ Unknown", "#f8f8f8"


def render_paper_source_badge(source_type, source_label, bg_color, paper_title):
    """Render a paper with source-colored badge."""
    return f"""
    <div style="background-color: {bg_color}; padding: 8px; border-radius: 5px; margin: 2px 0;">
        <strong style="color: green;">{source_label}</strong> 
        <span style="font-family: monospace;">{paper_title}</span>
    </div>
    """


def render_claim_card(item, uploaded_papers=None) -> None:
    uploaded_papers = uploaded_papers or []
    
    with st.container(border=True):
        # Determine claim source type
        claim_source_type, claim_source_label, claim_bg_color = get_paper_source_info(
            type('obj', (object,), {'paper_id': item.claim.source_paper_id})(),
            uploaded_papers
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
                        uploaded_papers
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
                        uploaded_papers
                    )
                    
                    st.markdown(
                        render_paper_source_badge(
                            evidence_source_type, evidence_source_label, "#ffe8e8",  # Red tint for contradicting
                            f"{snippet.title} (overlap={snippet.overlap_score})"
                        ),
                        unsafe_allow_html=True
                    )
                    st.error(f"> {snippet.sentence}")

            # Show hallucination-related papers with source info
            hallucination_terms = {"hallucination", "hallucinate", "unsupported", "factual", "grounding"}
            hallucination_sources = [
                e for e in item.evidence
                if hallucination_terms & set(e.sentence.lower().split())
                or hallucination_terms & set(e.title.lower().split())
            ]
            if hallucination_sources:
                st.markdown("**Papers claiming hallucination reduction**")
                for snippet in hallucination_sources:
                    source_type, source_label, bg_color = get_paper_source_info(
                        type('obj', (object,), {'paper_id': snippet.paper_id})(),
                        uploaded_papers
                    )
                    st.markdown(
                        render_paper_source_badge(
                            source_type, source_label, "#e8f4ff",  # Blue tint
                            f"{snippet.title}: {snippet.sentence}"
                        ),
                        unsafe_allow_html=True
                    )
        else:
            st.write("No evidence snippets available.")


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

    with st.sidebar:
        st.header("Demo Setup")
        corpus_choice = st.selectbox(
            "Corpus",
            (
                ("Final Demo Corpus", str(DEFAULT_CORPUS)),
                ("Sample Corpus", str(SAMPLE_CORPUS)),
            ),
            format_func=lambda option: option[0],
        )
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

    corpus_path = Path(corpus_choice[1])
    corpus_signature = compute_corpus_signature(corpus_path, uploaded_files)
    system, single_agent, rag, corpus, uploaded_papers, upload_errors = load_systems(
        corpus_path,
        uploaded_files,
        use_llm=bool(os.getenv("OPENAI_API_KEY")),
    )

    for message in upload_errors:
        st.sidebar.error(message)

    if run_clicked or st.session_state.get("last_run_signature") != corpus_signature:
        start_time = time.time()
        report = system.analyze_question(question)
        response_time = time.time() - start_time
        
        # Track accuracy metrics
        ACCURACY_TRACKER.log_query_performance(question, report, response_time)
        
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

        metrics = st.columns(3)
        metrics[0].metric("Claims Verified", len(report.verified_claims), help="Number of research claims extracted and verified")
        metrics[1].metric("Papers Retrieved", len(report.retrieved_papers), help="Total papers used from all sources (local + APIs)")
        metrics[2].metric("Critique Issues", len(report.critique_notes), help="Number of distinct issue categories flagged by the Critic Agent")

        with st.expander("Orchestration Trace", expanded=True):
            for step in report.iteration_trace:
                if step.startswith("Pass 2"):
                    st.markdown(f"🔁 `{step}`")
                else:
                    st.write(f"- {step}")

        with st.expander("Retrieved Papers", expanded=False):
            st.caption("Papers retrieved from uploaded files + live APIs (PubMed, arXiv) based on query relevance.")
            
            # Group papers by source for better presentation
            uploaded_retrieved = [p for p in report.retrieved_papers if p.paper_id in {up.paper_id for up in uploaded_papers}]
            api_retrieved = [p for p in report.retrieved_papers if p.paper_id.startswith(("PMC_", "ARXIV_"))]
            
            if uploaded_retrieved:
                st.markdown("**📤 From Uploaded Papers:**")
                for paper in uploaded_retrieved:
                    st.success(f"✅ **{paper.title}** ({paper.year}) — {', '.join(paper.authors)}")
            
            if api_retrieved:
                st.markdown("**🌐 From Live APIs:**")
                for paper in api_retrieved:
                    if paper.paper_id.startswith("PMC_"):
                        st.markdown(f"🏥 **PubMed**: {paper.title} ({paper.year}) — {', '.join(paper.authors)}")
                    elif paper.paper_id.startswith("ARXIV_"):
                        st.markdown(f"🔬 **arXiv**: {paper.title} ({paper.year}) — {', '.join(paper.authors)}")
            
            if not (uploaded_retrieved or api_retrieved):
                st.write("No papers were retrieved for this query.")
        
        # Optional debug section for uploaded papers (only show if papers were uploaded)
        if uploaded_papers:
            with st.expander(f"📤 Uploaded Papers ({len(uploaded_papers)} total)", expanded=False):
                st.caption("Papers uploaded this session (may or may not be used depending on query relevance)")
                for paper in uploaded_papers:
                    used_icon = "✅ Used" if paper.paper_id in {p.paper_id for p in report.retrieved_papers} else "⚪ Available"
                    st.write(f"- {used_icon} **{paper.title}** ({paper.year}) | {', '.join(paper.authors)}")

        # Add source breakdown summary - only 2 metrics for hybrid
        if report.retrieved_papers:
            with st.container():
                st.markdown("#### 📊 Source Analysis Summary")
                
                uploaded_count = len([p for p in report.retrieved_papers if p.paper_id in {up.paper_id for up in uploaded_papers}])
                api_count = len([p for p in report.retrieved_papers if p.paper_id.startswith(("PMC_", "ARXIV_"))])
                
                source_cols = st.columns(2)
                source_cols[0].metric("📤 Uploaded Papers Used", uploaded_count, help="Papers you uploaded that were relevant to the query")
                source_cols[1].metric("🌐 API Papers Retrieved", api_count, help="Papers fetched live from PubMed/arXiv APIs")
                
                if api_count > 0 and uploaded_count > 0:
                    st.success(f"✨ **Hybrid Mode Active**: Found {uploaded_count} uploaded papers + retrieved {api_count} from research databases")
                elif api_count > 0:
                    st.info(f"🌐 **API Mode**: Retrieved {api_count} papers from research databases (PubMed/arXiv)")
                elif uploaded_count > 0:
                    st.info(f"📤 **Uploaded Mode**: Using {uploaded_count} papers from your uploaded files")
                else:
                    st.warning("⚠️ **No Coverage**: No relevant papers found via uploads or APIs for this query")
        
        st.subheader("Verified Claims")
        
        for item in report.verified_claims:
            render_claim_card(item, uploaded_papers)

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
            accuracy_summary = ACCURACY_TRACKER.get_accuracy_summary()
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
                    "verified_claims": [asdict(item) for item in report.verified_claims],
                    "critique_notes": [asdict(item) for item in report.critique_notes],
                }
            )


if __name__ == "__main__":
    main()
