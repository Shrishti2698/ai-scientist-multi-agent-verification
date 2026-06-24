# AI-Scientist — Demo Cheat Sheet

Everything you need to drive the Streamlit UI: what's already loaded, what to ask, and **exactly which papers to upload for the best confidence scores**, with download links.

> See also: [docs/UI_OWNERSHIP.md](docs/UI_OWNERSHIP.md) for what every UI component means.

---

## 0. How it works (30-second version)

For any **research question or claim**, the system:
1. Checks it is research-oriented (rejects shopping/entertainment/personal queries).
2. Retrieves papers from **your uploads → the curated corpus → live PubMed/arXiv** (in that priority order).
3. Extracts claims, verifies each against evidence, runs a **critic re-check loop**, and writes a grounded report.
4. Shows the **multi-agent** result next to two baselines (single-agent, RAG).

Modes: **LLM mode** (verdicts + summary by your chosen GPT model) when `OPENAI_API_KEY` is set; **heuristic mode** offline fallback. Live retrieval is on in the UI; `NCBI_API_KEY` (set) raises the PubMed rate limit.

**Source priority (weightage): 📤 your uploads > 📚 curated corpus > 🌐 live APIs.** Uploading a relevant paper is the most reliable way to drive a high-confidence verdict.

---

## 1. Questions that work out-of-the-box (no upload needed)

These hit the built-in **Offline Demo Corpus** — 15 **real** paper abstracts (fetched from arXiv/PubMed) across 10 fields, used as an offline fallback/seed. Pick **"Offline Demo Corpus"** in the sidebar. For real analysis, upload papers or rely on live retrieval (both outrank this corpus).

| Domain | Ask |
|---|---|
| AI / CS | Do retrieval-augmented systems reduce hallucination in language models? |
| AI / CS | Do critic-guided verification loops improve research claim checking? |
| AI / CS | Is direct prompting alone sufficient for scientific verification? *(→ contradicted)* |
| Medicine | What is the best treatment for type 2 diabetes? |
| Medicine | Is telemedicine effective for rural healthcare delivery? |
| Biology | Does CRISPR gene therapy work for sickle cell disease? |
| Physics | Can quantum error correction work at room temperature in silicon qubits? |
| Psychology | Does social media usage increase depression in adolescents? |
| Neuroscience | Do brain-training apps improve cognition in older adults? |
| Economics | Does remote work improve productivity in large companies? |
| Education | Is online learning as effective as traditional classroom instruction? |
| Environment | Are solar panels more efficient than wind turbines? |
| Chemistry | Does green chemistry reduce toxic solvent use in drug manufacturing? |

**Off-scope demo (shows rejection):** "What is the best phone to buy this year?" · "What movie should I watch tonight?"

---

## 2. Query → upload **these papers** for the best confidence

Upload format reminder: open a link, grab the **title + abstract**, paste into a `.md` using the template in §4 (or upload the PDF directly). Upload 3–4 of the listed papers before asking the matching question — uploads outrank everything else, so confidence climbs.

### 🤖 AI / Computer Science

**Q: "Do retrieval-augmented systems reduce hallucination in language models?"**
→ Upload **A + B + C + D**:
- A. Lewis et al. (2020), *Retrieval-Augmented Generation for Knowledge-Intensive NLP* — https://arxiv.org/abs/2005.11401
- B. Shuster et al. (2021), *Retrieval Augmentation Reduces Hallucination in Conversation* — https://arxiv.org/abs/2104.07567
- C. Ji et al. (2022), *Survey of Hallucination in Natural Language Generation* — https://arxiv.org/abs/2202.03629
- D. Asai et al. (2023), *Self-RAG: Retrieve, Generate, and Critique via Self-Reflection* — https://arxiv.org/abs/2310.11511

**Q: "Do multi-agent systems improve scientific verification quality?"**
→ Upload:
- Du et al. (2023), *Improving Factuality and Reasoning via Multiagent Debate* — https://arxiv.org/abs/2305.14325
- Wadden et al. (2020), *Fact or Fiction: Verifying Scientific Claims (SciFact)* — https://arxiv.org/abs/2004.14974
- Dhuliawala et al. (2023), *Chain-of-Verification Reduces Hallucination* — https://arxiv.org/abs/2309.11495
- Min et al. (2023), *FActScore: Fine-grained Factual Precision* — https://arxiv.org/abs/2305.14251

**Q: "Is direct prompting alone sufficient for scientific verification?"** *(expect contradicted)*
→ Upload C + D above + Guu et al. (2020), *REALM* — https://arxiv.org/abs/2002.08909

### 🩺 Medicine

**Q: "What is the best treatment for type 2 diabetes?"**
→ Upload 3–4 of:
- ADA, *Standards of Care in Diabetes* (latest) — https://diabetesjournals.org/care/issue (Pharmacologic Approaches section, open access)
- Cochrane review, *Metformin monotherapy for type 2 diabetes* — search: https://www.cochranelibrary.com/search?text=metformin%20type%202%20diabetes
- UKPDS landmark trial — PubMed: https://pubmed.ncbi.nlm.nih.gov/?term=UKPDS+metformin+type+2+diabetes
- PMC full-text search: https://www.ncbi.nlm.nih.gov/pmc/?term=metformin+vs+insulin+type+2+diabetes

**Q: "Is telemedicine effective for rural healthcare delivery?"**
→ PMC: https://www.ncbi.nlm.nih.gov/pmc/?term=telemedicine+rural+healthcare+outcomes  ·  medRxiv: https://www.medrxiv.org/search/telemedicine%252Brural

### 🧬 Biology

**Q: "Does CRISPR gene therapy work for sickle cell disease?"**
→ Upload:
- Frangoul et al. (2021), *CRISPR-Cas9 Gene Editing for Sickle Cell Disease and β-Thalassemia* (NEJM) — https://www.ncbi.nlm.nih.gov/pmc/?term=CRISPR+CRISPR-Cas9+sickle+cell+Frangoul
- PMC search: https://www.ncbi.nlm.nih.gov/pmc/?term=CRISPR+gene+therapy+sickle+cell+disease
- bioRxiv: https://www.biorxiv.org/search/CRISPR%252Bsickle%252Bcell

### ⚛️ Physics

**Q: "Can quantum error correction work at room temperature in silicon qubits?"**
→ Upload:
- Devitt et al. (2013), *Quantum Error Correction for Beginners* — https://arxiv.org/abs/0905.2794
- Fowler et al. (2012), *Surface codes: Towards practical large-scale quantum computation* — https://arxiv.org/abs/1208.0928
- arXiv search (silicon/room-temp): https://arxiv.org/search/?searchtype=all&query=room+temperature+silicon+qubit+error+correction

### 🧠 Psychology / Neuroscience

**Q: "Does social media usage increase depression in adolescents?"**
→ PubMed: https://pubmed.ncbi.nlm.nih.gov/?term=social+media+depression+adolescents+longitudinal  ·  DOAJ: https://doaj.org/search/articles?source=%7B%22query%22%3A%7B%22query_string%22%3A%7B%22query%22%3A%22social%20media%20depression%20adolescents%22%7D%7D%7D

**Q: "Do brain-training apps improve cognition in older adults?"**
→ PubMed: https://pubmed.ncbi.nlm.nih.gov/?term=cognitive+training+older+adults+randomized  (e.g. the ACTIVE trial)

### 📈 Economics · 🎓 Education · 🌱 Environment · ⚗️ Chemistry

- Remote work productivity → NBER: https://www.nber.org/search?q=remote+work+productivity  ·  https://arxiv.org/a/econ
- Online vs classroom learning → ERIC: https://eric.ed.gov/?q=online+learning+meta-analysis  ·  DOAJ education search
- Solar vs wind efficiency → DOAJ: https://doaj.org/search/articles  (query "solar wind energy efficiency comparison")
- Green chemistry → PMC: https://www.ncbi.nlm.nih.gov/pmc/?term=green+chemistry+pharmaceutical+solvent

---

## 3. Where to download real papers (all free / open access)

| Source | URL | Best for |
|---|---|---|
| **arXiv** | https://arxiv.org | CS, AI/ML, physics, math (queried live) |
| **PubMed Central** | https://www.ncbi.nlm.nih.gov/pmc/ | Medicine, biology (queried live) |
| **Semantic Scholar** | https://www.semanticscholar.org | Any field; clean abstracts to copy |
| **bioRxiv / medRxiv** | https://www.biorxiv.org · https://www.medrxiv.org | Biology / medicine preprints |
| **DOAJ** | https://doaj.org | Open-access journals, all domains |
| **CORE** | https://core.ac.uk | Aggregated open-access PDFs |
| **OpenAlex** | https://openalex.org | Metadata + abstracts, all domains |
| **NBER** | https://www.nber.org | Economics working papers |
| **ERIC** | https://eric.ed.gov | Education research |

---

## 4. Upload formats

**Markdown / text** — metadata lines on top, then the abstract:
```
title: Your Paper Title
year: 2024
authors: A. Author, B. Author
topics: machine learning, evaluation

Abstract: The full abstract text containing the claims and results you want verified...
```

**JSON** — one paper or a list:
```json
{
  "paper_id": "MYPAPER1",
  "title": "Your Paper Title",
  "abstract": "Full abstract text with the key claims and results...",
  "year": 2024,
  "authors": ["A. Author"],
  "topics": ["topic1", "topic2"]
}
```

**PDF** — works directly (pypdf installed). The **abstract is what gets verified**, so make sure it's present.

---

## 5. Getting interesting verdicts on purpose

- **Supported, high confidence:** upload 3–4 on-topic papers from §2, then ask the matching question.
- **Contradicted:** assert an overclaim ("Retrieval always eliminates hallucination regardless of relevance") — the critic loop pushes back.
- **Insufficient evidence:** ask a niche question with no matching paper — the system declines to overclaim (a feature).
- **See the critic loop:** open **🛰️ Orchestration Trace** and look for the 🔁 "Pass 2 revisited…" line.
- **Multi-agent vs baselines:** compare the left report to the right-column Single-Agent / RAG verdicts.

---

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| "No relevant papers found" | Topic not in corpus and live APIs returned nothing — upload a paper from §2, or rephrase with the title's key terms. |
| Live medical query is slow | Live PubMed call + rate limiting; with `NCBI_API_KEY` (set) it's faster. arXiv can time out and is skipped gracefully. |
| Verdicts look heuristic, not LLM | `OPENAI_API_KEY` missing/invalid in `.env`. LLM failures now log a warning and fall back. |
| Want fully offline / reproducible | Works without network; only live-retrieval augmentation needs it. |

---

## 7. Run commands

```powershell
$env:PYTHONPATH = 'src'
streamlit run app.py                  # the UI
uvicorn ai_scientist.api:app --reload # REST API
python -m unittest discover -s tests  # 32 tests, ~7s
```
