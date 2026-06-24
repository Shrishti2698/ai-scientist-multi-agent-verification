# UI Ownership — Streamlit App (`app.py`)

A component-by-component reference for the AI-Scientist Streamlit interface: what each element is, where it comes from in the code, and what it means. Use this for demos, debugging, and onboarding.

Launch: `$env:PYTHONPATH='src'; streamlit run app.py` → http://localhost:8501

---

## Layout overview

```
┌───────────────┬───────────────────────────────────────┬──────────────────────┐
│  SIDEBAR      │  LEFT COLUMN (Multi-Agent Report)      │ RIGHT COLUMN          │
│  (Demo Setup) │  - Summary + 3 metrics                 │ (Baseline Snapshot)   │
│  - Corpus     │  - Orchestration Trace                 │ - Single-Agent        │
│  - LLM model  │  - Retrieved Papers (by source)        │ - RAG baseline        │
│  - Upload     │  - Uploaded Papers                     │ - Accuracy metrics    │
│  - Question   │  - Source Analysis Summary             │ - Critique Notes      │
│  - Run button │  - Verified Claims (cards)             │ - Structured JSON     │
└───────────────┴───────────────────────────────────────┴──────────────────────┘
```

The page is rendered top-to-bottom by `main()` in [app.py](../app.py). Streamlit re-runs the whole script on every interaction; results persist between runs via `st.session_state`.

---

## 1. Sidebar — "Demo Setup"

| Component | Purpose | Code |
|---|---|---|
| **Corpus** dropdown | Picks the built-in grounding corpus. **Offline Demo Corpus** (15 **real** abstracts from arXiv/PubMed, 10 fields) is the default offline fallback/seed; **AI/CS Sample Corpus** is the narrow 6-paper test fixture. Uploaded papers are merged into whichever you pick and rank above it. | `corpus_choice` |
| **LLM model** dropdown | Selects the OpenAI model used for verification + summary, with an approximate per-call cost. Disabled (greyed) if no `OPENAI_API_KEY`. Options: GPT-5.5 / 5.4 / 5.4-mini / 4o / 4o-mini. | `MODEL_OPTIONS`, `model_choice` |
| caption under model | Shows the active model + approx cost, or a prompt to set the API key. | — |
| **Upload paper(s)** | Drag-and-drop `.md`/`.txt`/`.json`/`.pdf`. Uploaded papers join the active corpus **for that session** and are ranked **above** corpus and API papers. | `st.file_uploader`, `RawPaperIngestor` |
| **Research question** | The question or claim to analyze. | `question` text area |
| **Run Analysis** | Triggers a fresh analysis. Analysis also auto-runs when corpus/model/uploads change. | `run_clicked` |

---

## 2. Left column — "Multi-Agent Report"

This is the output of the full multi-agent pipeline ([orchestrator.py](../src/ai_scientist/agents/orchestrator.py)).

### 2.1 Summary
A 2–4 sentence grounded conclusion. In LLM mode it is written by the selected model; in heuristic mode it is templated. Source: `SynthesisAgent`.

### 2.2 Three metrics
| Metric | Meaning |
|---|---|
| **Claims Verified** | How many individual claims were extracted from the retrieved papers and verified. |
| **Papers Retrieved** | Total papers grounding the analysis = uploaded + curated corpus + live API. **This counts ALL sources** — if it's >0 you *did* retrieve papers (the per-source breakdown below shows from where). |
| **Critique Issues** | Number of issue categories the Critic Agent flagged (e.g. single-source claims, overgeneralization). |

### 2.3 🛰️ Orchestration Trace (`render_orchestration_trace`)
The step-by-step path the agents took. Always shows the **agent pipeline legend**:

`🔍 Retrieval → 🧩 Claim Extraction → ✅ Verification → 🧐 Critic → 🔁 Targeted Re-verification → 📝 Synthesis`

Then a numbered trace. Icons: 🔍 retrieval, 🧩 claim extraction, 🧐 critic, 🔁 second-pass re-verification (offset as a quote block), 🛑 stopped early (out of scope / no papers). The 🔁 lines are the key research contribution — the critic loop asking for a targeted re-check.

### 2.4 Retrieved Papers (expander)
Every grounding paper, grouped by source:
- **📤 From your uploads** — highest priority.
- **📚 From the curated corpus** — built-in offline papers (e.g. `MED001`, `P1`).
- **🌐 From live research databases** — 🏥 PubMed (`PMC_…`) / 🔬 arXiv (`ARXIV_…`).

> Source is decided by `get_paper_source_info()` using the paper id and the uploaded/corpus id sets. A paper that is in none of these would show "❓ Unknown" — that should not happen now that corpus ids are passed in.

### 2.5 Uploaded Papers (expander, only if you uploaded)
Lists every uploaded paper with **✅ Used** or **⚪ Available** depending on whether it was relevant enough to retrieve for this query.

### 2.6 📊 Source Analysis Summary
Three counters — **📤 Uploaded / 📚 Curated Corpus / 🌐 Live APIs** — plus a one-line "Grounded on …" sentence. This is the per-source breakdown of the "Papers Retrieved" metric.

### 2.7 Verified Claims (cards, `render_claim_card`)
One bordered card per claim:
- **Claim text** (heading).
- **Source badge** — colored chip showing where the claim came from (📤/📚/🏥/🔬).
- **Verdict** (`supported` / `contradicted` / `insufficient_evidence` / `out_of_scope`) and **Confidence** (0–1).
- **Type / Focus** caption (claim type + focus terms).
- **Rationale** — why the verdict was reached.
- **Supporting Evidence** (green) / **Contradicting Sources** (red) — the exact sentences and their source badges, with overlap scores.

---

## 3. Right column — "Baseline Snapshot"

For research comparison against the multi-agent system.

| Block | Purpose |
|---|---|
| **Single-Agent Baseline** | Trusts the single top-ranked paper. Verdict + confidence + rationale. |
| **RAG Baseline** | Standard retrieve-then-check over top-k; no explicit contradiction analysis. |
| **System Accuracy Metrics** | Running stats across this session: Retrieval Success %, Claim Extraction %, Avg Confidence, Response Time. Source: `AccuracyCalculator`. |
| **Critique Notes** | Full critic output with severity icons 🔴 high / 🟡 medium / 🟢 low. |
| **Structured JSON View** | The raw report object (question, summary, retrieved_papers, verified_claims, critique_notes, iteration_trace) for copy/paste and debugging. |

---

## 4. Verdict glossary

| Verdict | Meaning |
|---|---|
| `supported` | Evidence in the grounding papers backs the claim. |
| `contradicted` | Strong counter-evidence found (critic loop often surfaces this on the second pass). |
| `insufficient_evidence` | Not enough aligned evidence; the system deliberately does **not** overclaim. |
| `out_of_scope` | Non-research / commercial / entertainment query — rejected before retrieval. |

---

## 5. Common "is this a bug?" answers

- **"Papers Retrieved: 2" but I only see corpus papers, no API papers** — expected. The metric counts all sources; if the live APIs returned nothing (rate limit/timeout) you're grounded on the curated corpus, which is fine.
- **A claim shows source 📚 Curated Corpus** — correct; that claim was extracted from a built-in paper.
- **Confidence varies between claims** — intended; confidence is calibrated per claim by evidence strength and corroboration.
- **Uploaded paper not shown as "Used"** — it wasn't relevant enough to the query (below the coverage threshold). Rephrase using the paper's key terms.
