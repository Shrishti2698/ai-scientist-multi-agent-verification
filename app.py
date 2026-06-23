from __future__ import annotations

import hashlib
import os
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


ROOT = Path(__file__).resolve().parent
DEFAULT_CORPUS = ROOT / "data" / "final_demo_corpus.json"
SAMPLE_CORPUS = ROOT / "data" / "sample_corpus.json"
INGESTOR = RawPaperIngestor()

load_environment()


def build_active_corpus(corpus_path: Path, uploaded_files=None):
    corpus = CorpusRepository.from_path(corpus_path)
    uploaded_papers = []
    upload_errors: list[str] = []

    for uploaded_file in uploaded_files or []:
        try:
            uploaded_papers.extend(INGESTOR.ingest_uploaded(uploaded_file.name, uploaded_file.getvalue()))
        except IngestionError as exc:
            upload_errors.append(f"{uploaded_file.name}: {exc}")

    combined_papers = corpus.all_papers() + uploaded_papers
    deduped_papers = []
    seen_ids: set[str] = set()
    for paper in combined_papers:
        if paper.paper_id in seen_ids:
            continue
        deduped_papers.append(paper)
        seen_ids.add(paper.paper_id)

    return CorpusRepository(deduped_papers), uploaded_papers, upload_errors


def compute_corpus_signature(corpus_path: Path, uploaded_files=None) -> str:
    digest = hashlib.sha256(str(corpus_path).encode("utf-8"))
    for uploaded_file in uploaded_files or []:
        digest.update(uploaded_file.name.encode("utf-8"))
        digest.update(uploaded_file.getvalue())
    return digest.hexdigest()


def load_systems(corpus_path: Path, uploaded_files=None, use_llm: bool = False):
    corpus, uploaded_papers, upload_errors = build_active_corpus(corpus_path, uploaded_files)
    settings = Settings(enable_openai_llm=use_llm)
    return (
        MultiAgentResearchSystem(settings=settings, corpus=corpus),
        SingleAgentBaseline(settings=settings, corpus=corpus),
        RagBaseline(settings=settings, corpus=corpus),
        corpus,
        uploaded_papers,
        upload_errors,
    )


def render_claim_card(item) -> None:
    with st.container(border=True):
        st.subheader(item.claim.text)
        left, right = st.columns(2)
        left.metric("Verdict", item.verdict)
        right.metric("Confidence", f"{item.confidence:.3f}")
        st.caption(
            f"Type: {item.claim.claim_type} | Claim source: **{item.claim.source_title}**"
        )
        if item.claim.focus_terms:
            st.write(f"Focus terms: {', '.join(item.claim.focus_terms)}")
        st.write(item.rationale)

        if item.evidence:
            supporting = [e for e in item.evidence if item.verdict != "contradicted"]
            contradicting = [e for e in item.evidence if item.verdict == "contradicted"]

            if supporting:
                st.markdown("**Supporting Evidence** (papers that back this claim)")
                for snippet in supporting:
                    st.success(
                        f"📄 **{snippet.title}** (overlap={snippet.overlap_score})\n\n"
                        f"> {snippet.sentence}"
                    )

            if contradicting:
                st.markdown("**Contradicting / Verification Sources**")
                for snippet in contradicting:
                    st.error(
                        f"📄 **{snippet.title}** (overlap={snippet.overlap_score})\n\n"
                        f"> {snippet.sentence}"
                    )

            hallucination_terms = {"hallucination", "hallucinate", "unsupported", "factual", "grounding"}
            hallucination_sources = [
                e for e in item.evidence
                if hallucination_terms & set(e.sentence.lower().split())
                or hallucination_terms & set(e.title.lower().split())
            ]
            if hallucination_sources:
                st.markdown("**Papers claiming hallucination reduction**")
                for snippet in hallucination_sources:
                    st.info(f"🔬 **{snippet.title}**: {snippet.sentence}")
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
        "Interactive multi-agent research verification demo over the frozen offline corpus."
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
        report = system.analyze_question(question)
        st.session_state["last_report"] = report
        st.session_state["baseline_single"] = single_agent.verify_claim(question)
        st.session_state["baseline_rag"] = rag.verify_claim(question)
        st.session_state["last_run_signature"] = corpus_signature
    else:
        report = st.session_state["last_report"]

    left, right = st.columns([1.35, 1])

    with left:
        st.subheader("Multi-Agent Report")
        if not report.verified_claims and "validated only for AI and computer science" in report.summary:
            st.warning(report.summary)
        st.write(report.summary)

        metrics = st.columns(4)
        metrics[0].metric("Claims Verified", len(report.verified_claims))
        metrics[1].metric("Critique Issues", len(report.critique_notes), help="Number of distinct issue categories flagged by the Critic Agent")
        metrics[2].metric("Retrieved Papers", len(report.retrieved_papers))
        metrics[3].metric("Corpus Papers", len(corpus.all_papers()), help="Fixed offline papers downloaded locally; not fetched per query")

        with st.expander("Orchestration Trace", expanded=True):
            for step in report.iteration_trace:
                if step.startswith("Pass 2"):
                    st.markdown(f"🔁 `{step}`")
                else:
                    st.write(f"- {step}")

        with st.expander("Retrieved Papers", expanded=False):
            for paper in report.retrieved_papers:
                st.write(f"- `{paper.title}` ({paper.year}) — {', '.join(paper.authors)}")

        with st.expander(
            f"Corpus Papers ({len(corpus.all_papers())} total papers in active corpus)",
            expanded=False,
        ):
            st.caption(
                "These papers are stored locally in the active corpus. "
                "Uploaded papers are merged with the frozen demo corpus for this session."
            )
            for paper in corpus.all_papers():
                st.write(
                    f"- **{paper.title}** ({paper.year}) "
                    f"| {', '.join(paper.authors)} "
                    f"| Topics: {', '.join(paper.topics)}"
                )

        if uploaded_papers:
            with st.expander("Uploaded Papers", expanded=False):
                st.caption("These papers were uploaded during this session and merged into the active corpus.")
                for paper in uploaded_papers:
                    st.write(f"- **{paper.title}** ({paper.year}) | {', '.join(paper.authors)}")

        st.subheader("Verified Claims")
        for item in report.verified_claims:
            render_claim_card(item)

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
            st.markdown("**Critique Notes**")
            if report.critique_notes:
                severity_colors = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                for note in report.critique_notes:
                    icon = severity_colors.get(note.severity, "ℹ️")
                    st.warning(f"{icon} **{note.severity.upper()}**: {note.message}")
            else:
                st.write("No critique issues identified in this pass.")

        with st.expander("Raw Report Markdown", expanded=False):
            st.code(report.markdown, language="markdown")

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
