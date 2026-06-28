from __future__ import annotations

from html import escape
from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository


class DemoAssetBuilder:
    def build_html_report(self, corpus_path: str | Path, question: str) -> str:
        corpus = CorpusRepository.from_path(corpus_path)
        system = MultiAgentResearchSystem(settings=Settings(), corpus=corpus)
        report = system.analyze_question(question)

        claim_cards = []
        for item in report.verified_claims:
            evidence_html = "".join(
                f"<li><strong>{escape(snippet.title)}</strong>: {escape(snippet.sentence)} "
                f"<em>(overlap={snippet.overlap_score})</em></li>"
                for snippet in item.evidence
            ) or "<li>No evidence snippets</li>"
            claim_cards.append(
                f"""
                <section class="card">
                  <h3>{escape(item.claim.text)}</h3>
                  <p><strong>Type:</strong> {escape(item.claim.claim_type)} | <strong>Verdict:</strong> {escape(item.verdict)} | <strong>Confidence:</strong> {item.confidence}</p>
                  <p><strong>Source:</strong> {escape(item.claim.source_title)}</p>
                  <p>{escape(item.rationale)}</p>
                  <ul>{evidence_html}</ul>
                </section>
                """
            )

        trace_html = "".join(f"<li>{escape(step)}</li>" for step in report.iteration_trace) or "<li>No trace</li>"
        notes_html = "".join(
            f"<li><strong>{escape(note.severity)}</strong>: {escape(note.message)} ({escape(note.claim)})</li>"
            for note in report.critique_notes
        ) or "<li>No critique notes</li>"

        return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AI-Scientist Demo Report</title>
  <style>
    :root {{ --bg:#f5f1e8; --ink:#1e2430; --accent:#0d6b6b; --card:#fffdf8; --border:#d8cfbf; }}
    body {{ margin:0; font-family: Georgia, 'Times New Roman', serif; background:linear-gradient(135deg,#f5f1e8,#e6efe9); color:var(--ink); }}
    main {{ max-width: 980px; margin: 0 auto; padding: 32px 20px 48px; }}
    h1,h2,h3 {{ margin:0 0 12px; }}
    .hero {{ padding:24px; background:rgba(255,253,248,.85); border:1px solid var(--border); border-radius:20px; box-shadow:0 10px 30px rgba(0,0,0,.06); }}
    .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:16px; margin-top:20px; }}
    .card {{ background:var(--card); border:1px solid var(--border); border-radius:16px; padding:18px; box-shadow:0 8px 24px rgba(0,0,0,.05); }}
    ul {{ padding-left:20px; }}
    .muted {{ color:#4d5a65; }}
  </style>
</head>
<body>
  <main>
    <section class="hero">
      <h1>AI-Scientist Demo Report</h1>
      <p><strong>Question:</strong> {escape(report.question)}</p>
      <p class="muted">{escape(report.summary)}</p>
    </section>
    <section class="grid">
      <section class="card">
        <h2>Orchestration Trace</h2>
        <ul>{trace_html}</ul>
      </section>
      <section class="card">
        <h2>Critique Notes</h2>
        <ul>{notes_html}</ul>
      </section>
    </section>
    <section style="margin-top:20px;">
      <h2>Verified Claims</h2>
      <div class="grid">
        {''.join(claim_cards)}
      </div>
    </section>
    <section class="card" style="margin-top:20px;">
      <h2>Final Answer</h2>
      <p>{escape(report.summary)}</p>
    </section>
  </main>
</body>
</html>
"""

    def export_html_report(self, corpus_path: str | Path, question: str, output_path: str | Path) -> None:
        Path(output_path).write_text(self.build_html_report(corpus_path, question), encoding="utf-8")
