# Phase 9: Experiment Runner and Result Artifacts

## Goal

Turn evaluation into a repeatable workflow that produces thesis-friendly outputs instead of only terminal logs.

## Why this matters

Panel members will care about methodology and results. A reproducible experiment runner helps answer:

- what systems were compared,
- on which benchmark,
- with what metrics,
- and what the outputs looked like.

## Current implementation

The repository now supports an experiment run that exports:

- machine-readable JSON summaries,
- case-level CSV results,
- and a markdown report.

## Research use

This creates the foundation for:

- result tables in the dissertation,
- ablation studies,
- tracked improvements across versions,
- and easier comparison when the corpus expands.
