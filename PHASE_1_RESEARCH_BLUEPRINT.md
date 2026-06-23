# Phase 1: Research Blueprint for AI-Scientist

## 1. Project Positioning

This project should be presented as a research-oriented system, not only as an engineering implementation of multiple agents. The main research goal is to study whether a multi-agent orchestrated framework improves scientific claim verification and adaptive reasoning compared to simpler alternatives.

The system will focus on AI and computer science research papers in the first version. This narrower scope makes the project feasible, easier to evaluate, and stronger during thesis defense.

## 2. Core Research Problem

Large language models can generate fluent research answers, but they often:

- produce unsupported claims,
- hallucinate citations or facts,
- fail to reason carefully across multiple papers,
- and do not explicitly critique their own conclusions.

The research problem for this project is:

Can a multi-agent orchestrated framework improve the reliability and traceability of scientific claim verification for AI and computer science research papers compared to a single-agent LLM and a standard RAG pipeline?

## 3. Research Hypothesis

### Main Hypothesis

A multi-agent orchestrated framework with dedicated retrieval, claim extraction, verification, critique, and synthesis stages will produce more reliable and evidence-backed outputs than:

- a direct single-agent LLM baseline, and
- a standard RAG-based baseline.

### Sub-Hypotheses

- Explicit claim verification reduces hallucinated or unsupported statements.
- A critic stage improves reasoning consistency by identifying weak evidence and contradictions.
- Orchestrated decomposition improves citation quality and evidence coverage.

## 4. Research Scope

### Included in Scope

- AI and computer science research papers.
- Research question answering and claim verification.
- Evidence-backed report generation.
- Confidence estimation at claim or response level.
- Experimental comparison against baseline systems.

### Out of Scope for Initial Version

- All scientific domains.
- Multi-modal reasoning over figures and tables.
- Automatic paper writing.
- Full human-in-the-loop workflow.
- Large-scale production deployment.

## 5. System Goal

Given a research question or claim, the system should:

1. retrieve relevant research papers,
2. extract important claims and findings,
3. verify those claims using supporting or contradictory evidence,
4. critique weak or incomplete reasoning,
5. synthesize validated evidence,
6. produce a final report with sources and confidence.

## 6. First-Version System Boundary

The first working version should be an MVP research prototype with the following agents:

- `Orchestrator Agent`
- `Literature Retrieval Agent`
- `Claim Extraction Agent`
- `Verification Agent`
- `Report Generation Agent`

The `Critic Agent` should be added in a second iteration after the first pipeline works end-to-end.

This staged design is important because the research contribution depends on comparing controlled versions of the system, not on building every feature at once.

## 7. Research Contribution

The likely contribution statement for this MTech project is:

"A domain-focused multi-agent framework for scientific claim verification over AI and computer science literature, with empirical comparison against single-agent and standard RAG baselines."

This contribution has three parts:

- a system contribution: the orchestrated multi-agent architecture,
- an evaluation contribution: controlled comparison with baselines,
- an analysis contribution: identifying where orchestration helps and where it fails.

## 8. Baseline Systems

To make the project defensible as research, at least two baselines should be implemented.

### Baseline 1: Single-Agent LLM

A single LLM answers the research question directly from its own reasoning, optionally with the paper titles or abstracts provided in prompt context.

Purpose:

- measures performance without explicit orchestration,
- establishes the simplest comparison point.

### Baseline 2: Standard RAG

A conventional retrieval-augmented generation system retrieves relevant documents and asks a single LLM to answer using the retrieved context.

Purpose:

- measures whether retrieval alone is enough,
- compares standard modern pipeline behavior against multi-agent orchestration.

### Proposed System: Multi-Agent AI-Scientist

The orchestrator coordinates specialized agents for retrieval, extraction, verification, and reporting.

Purpose:

- tests whether task decomposition improves research verification quality.

## 9. Evaluation Questions

The evaluation should answer these research questions:

1. Does the multi-agent system reduce hallucinated or unsupported claims?
2. Does it improve evidence coverage compared to baseline systems?
3. Does it produce more consistent and traceable reasoning?
4. Does adding a critic stage improve final output quality?

## 10. Evaluation Metrics

The metrics should be both quantitative and qualitative.

### Quantitative Metrics

- `Claim Verification Accuracy`
- `Hallucination Rate`
- `Evidence Coverage`
- `Citation Quality`
- `Reasoning Consistency`
- `Response Completeness`

### Operational Definitions

- `Claim Verification Accuracy`: percentage of extracted claims correctly labeled as supported, contradicted, or insufficient evidence.
- `Hallucination Rate`: percentage of response statements not grounded in retrieved evidence.
- `Evidence Coverage`: fraction of important answer claims linked to relevant supporting sources.
- `Citation Quality`: correctness and relevance of cited papers for the generated conclusions.
- `Reasoning Consistency`: whether the final answer aligns with the evidence gathered across steps.
- `Response Completeness`: whether the answer addresses the main parts of the original research query.

### Qualitative Analysis

- failure cases,
- contradiction handling behavior,
- weak retrieval cases,
- agent coordination errors,
- and comparison of outputs across systems.

## 11. Dataset and Corpus Strategy

For Phase 1, the safest choice is a focused AI/CS paper corpus.

### Recommended Initial Corpus

- a curated set of AI and computer science papers,
- primarily abstracts first,
- then full papers if needed in later phases.

### Possible Source Options

- Semantic Scholar dataset or API-backed paper selection,
- arXiv papers in selected subdomains,
- manually curated benchmark papers for controlled evaluation.

### Recommended Starting Strategy

Start with a small curated corpus such as:

- machine learning,
- large language models,
- retrieval-augmented generation,
- agentic systems,
- hallucination mitigation.

This makes debugging easier and helps create a reliable evaluation set.

## 12. Expected Deliverables for Phase 1

By the end of Phase 1, the project should have:

- a finalized research problem statement,
- a defined scope and domain,
- baseline definitions,
- evaluation criteria,
- initial system boundary for the MVP,
- and a phase-wise implementation roadmap.

## 13. Risks and Early Mitigations

### Risk 1: Scope becomes too broad

Mitigation:

- restrict to AI and CS papers,
- begin with abstracts or selected papers,
- avoid multi-domain claims in the thesis.

### Risk 2: Research contribution appears weak

Mitigation:

- focus on comparative experiments,
- design measurable metrics,
- include ablation studies and failure analysis.

### Risk 3: Too much engineering, not enough evaluation

Mitigation:

- build baselines early,
- collect evaluation samples early,
- keep the MVP small and experiment-friendly.

### Risk 4: Agent complexity slows progress

Mitigation:

- start with fewer agents,
- add the critic and iterative loops later,
- validate each stage independently.

## 14. Recommended Phase Breakdown

### Phase 1: Research Blueprint

- finalize scope, hypothesis, baselines, metrics, and deliverables.

### Phase 2: Project Setup and Corpus Preparation

- create codebase structure,
- choose libraries,
- collect and normalize the first paper corpus.

### Phase 3: Baseline Implementations

- implement single-agent baseline,
- implement standard RAG baseline.

### Phase 4: Multi-Agent MVP

- implement orchestrator, retrieval, claim extraction, verification, and reporting.

### Phase 5: Critic and Iterative Reasoning

- add critic feedback and second-pass verification loops.

### Phase 6: Evaluation and Ablations

- compare systems,
- run metric-based experiments,
- analyze error patterns.

### Phase 7: Thesis and Demo Preparation

- prepare diagrams,
- document methodology,
- create presentation-ready outputs.

## 15. Immediate Next Step

Phase 2 should begin by defining the project structure and technical stack in implementation terms:

- backend architecture,
- agent interfaces,
- retrieval pipeline design,
- corpus format,
- and experiment folder structure.

That step should keep the research goals visible so the implementation does not drift into a generic chatbot project.
