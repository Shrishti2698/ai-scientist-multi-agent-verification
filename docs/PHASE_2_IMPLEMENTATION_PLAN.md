# Phase 2: Implementation Plan

## Objective

Translate the research blueprint into a codebase that is small enough to build quickly and structured enough for experiments.

## Deliverables

- package structure for agents, baselines, and evaluation,
- sample corpus and benchmark claims,
- FastAPI endpoints,
- deterministic MVP workflow that runs without external APIs.

## Core Decisions

- Domain: AI and computer science literature only.
- First artifact: backend research prototype.
- Corpus strategy: curated local JSON corpus first.
- Agent execution: deterministic and inspectable before adding external LLM calls.

## Technical Stack

- Python
- FastAPI
- Pydantic
- JSON-based local corpus

## Architecture

- `CorpusRepository` manages paper data.
- `RetrievalAgent` ranks papers for a query.
- `ClaimExtractionAgent` proposes important claims.
- `VerificationAgent` assigns verdicts with evidence.
- `CriticAgent` flags weak reasoning and unsupported claims.
- `SynthesisAgent` builds a response narrative.
- `ReportGenerationAgent` emits a structured markdown report.
- `MultiAgentResearchSystem` orchestrates the workflow.

## Success Criteria

- One question produces an end-to-end report.
- One claim can be verified independently.
- Baselines and multi-agent pipeline share the same corpus.
- Benchmark evaluation runs from the command line or API.

