# AI-Scientist Project Ownership

## 1. Project Summary

AI-Scientist is an MTech research project for AI and computer science literature verification.
It takes a research question, retrieves relevant papers from a corpus, extracts claims, verifies them against evidence, critiques weak reasoning, and produces a readable report in Streamlit.

The project is intentionally scoped to AI and computer science.
Out-of-scope questions from medicine, law, finance, or other domains are rejected early so the demo does not give misleading confidence.

## 2. What Makes It A Research Project

The contribution is not just a chatbot or a plain RAG demo.
The research angle is the comparison of multiple verification strategies:

- Single-agent baseline
- RAG baseline
- Multi-agent verification pipeline
- Critic-guided second pass

The benchmark, ablation studies, and failure analysis are what make the project thesis-friendly.

## 3. Current Architecture

### UI Layer

- File: `app.py`
- Tool: Streamlit
- Purpose: lets the user choose a corpus, upload a paper, enter a question, and inspect the report

### API Layer

- File: `src/ai_scientist/api.py`
- Tool: FastAPI
- Purpose: exposes analyze and verify endpoints for programmatic use

### Core Pipeline

- File: `src/ai_scientist/agents/orchestrator.py`
- Purpose: coordinates retrieval, claim extraction, verification, critique, and synthesis

### Retrieval

- File: `src/ai_scientist/agents/retrieval.py`
- Model: none
- Method: lexical overlap retrieval over the local corpus

### Claim Extraction

- File: `src/ai_scientist/agents/claim_extraction.py`
- Model: none
- Method: rule-based sentence selection and claim typing

### Verification

- File: `src/ai_scientist/agents/verification.py`
- Model: OpenAI-backed `OpenAIResearchLLM` when `OPENAI_API_KEY` is available
- Fallback: heuristic verifier if the API key, SDK, or request fails

### Critic

- File: `src/ai_scientist/agents/critic.py`
- Model: none
- Method: heuristic critique and re-verification targeting

### Synthesis

- File: `src/ai_scientist/agents/synthesis.py`
- Model: OpenAI-backed `OpenAIResearchLLM` when available
- Fallback: deterministic summary builder

### Report Generation

- File: `src/ai_scientist/agents/report.py`
- Model: none
- Method: deterministic markdown and structured report assembly

## 4. Model Map

| Component | Model/Technique | Notes |
| --- | --- | --- |
| RetrievalAgent | None | Keyword and overlap scoring only |
| ClaimExtractionAgent | None | Rule-based |
| VerificationAgent | `Settings.openai_model` via `OpenAIResearchLLM` | Uses structured outputs when API is available |
| CriticAgent | None | Heuristic critique and reroute decisions |
| SynthesisAgent | `Settings.openai_model` via `OpenAIResearchLLM` | Produces a concise final summary when API is available |
| SingleAgentBaseline | None | Baseline comparator |
| RagBaseline | None | Baseline comparator |
| ReportGenerationAgent | None | Deterministic formatting |

Current default model value is defined in `src/ai_scientist/config.py`.
If the API key or SDK is unavailable, the project still runs using heuristic fallback.

## 5. Data Flow

1. The user selects a frozen corpus or uploads a paper.
2. The active corpus is built by merging the selected corpus with any uploaded papers.
3. Retrieval finds the most relevant papers for the question.
4. Claim extraction turns the question and retrieved abstracts into structured claims.
5. Verification checks support and contradiction evidence.
6. The critic flags weak support, single-source claims, and contradiction cases.
7. The synthesis stage creates the final summary.
8. The report is shown in the Streamlit UI and can be exported for thesis use.

## 6. Corpus Strategy

### Frozen Demo Corpus

- Used for stable presentations and reproducible evaluation
- Lives in `data/final_demo_corpus.json`

### Uploaded Papers

- Uploaded via the Streamlit sidebar
- Parsed with `RawPaperIngestor`
- Merged into the active corpus for the current session

### Supported Upload Types

- `.md`
- `.txt`
- `.json`
- `.pdf` with `pypdf`

## 7. Runtime Modes

### Offline Demo Mode

- Uses the frozen corpus
- Avoids external data dependence
- Best for panel demo day

### OpenAI-Backed Mode

- Activated when `OPENAI_API_KEY` is available and the runtime enables LLM mode
- Uses structured LLM calls for verification and synthesis
- Falls back automatically if the call fails

## 8. What To Run

- Streamlit UI: `py -3 -m streamlit run app.py`
- API: `py -3 -m uvicorn ai_scientist.api:app --reload`
- Tests: `py -3 -m unittest`

## 9. Key Files To Know

- [`app.py`](C:\Users\USER\Documents\4thsemproject\app.py)
- [`src/ai_scientist/agents/orchestrator.py`](C:\Users\USER\Documents\4thsemproject\src\ai_scientist\agents\orchestrator.py)
- [`src/ai_scientist/agents/verification.py`](C:\Users\USER\Documents\4thsemproject\src\ai_scientist\agents\verification.py)
- [`src/ai_scientist/agents/synthesis.py`](C:\Users\USER\Documents\4thsemproject\src\ai_scientist\agents\synthesis.py)
- [`src/ai_scientist/llm.py`](C:\Users\USER\Documents\4thsemproject\src\ai_scientist\llm.py)
- [`src/ai_scientist/ingestion.py`](C:\Users\USER\Documents\4thsemproject\src\ai_scientist\ingestion.py)
- [`docs/LLM_UPGRADE_PLAN.md`](C:\Users\USER\Documents\4thsemproject\docs\LLM_UPGRADE_PLAN.md)

## 10. Thesis Story

If asked what the project contributes, the shortest honest answer is:

- It compares a naive baseline, a RAG baseline, and a multi-agent verification pipeline.
- It adds a critic loop to detect weak or contradictory evidence.
- It uses OpenAI-backed structured outputs for the parts that benefit from language understanding.
- It keeps a frozen corpus and evaluation harness so the results are reproducible.

## 11. Maintenance Rules

- Keep AI/CS scope enforcement active.
- Preserve the frozen corpus for the main demo.
- Keep uploaded papers as an additive feature, not a replacement for the base corpus.
- Keep the baselines intact so the research comparison remains valid.
- Prefer changes in agents or helper services instead of pushing logic into the UI.
- Treat report wording as part of the demo contract because it is what the panel sees first.
