# Phase 3: Baselines and Evaluation

## Baselines

### Single-Agent Baseline

Uses the best matching paper and a direct heuristic assessment without explicit multi-step verification.

### Standard RAG Baseline

Retrieves multiple relevant papers and synthesizes evidence, but does not use claim-level critique or orchestration.

## Evaluation Strategy

The benchmark should contain claims with expected verdicts:

- `supported`
- `contradicted`
- `insufficient_evidence`

## Early Metrics

- verification accuracy,
- average confidence,
- evidence coverage,
- citation quality proxy,
- and contradiction sensitivity.

## Why this matters

These baselines create the actual research comparison. Without them, the project risks looking like system design without scientific evaluation.

