# Phase 8: Corpus Ingestion and Growth

## Goal

Move from a tiny handcrafted benchmark corpus toward a reusable research collection pipeline.

## Why this matters

A serious MTech project needs experiments on more than a few manually typed examples. Corpus ingestion is the bridge between a prototype and a defendable evaluation setup.

## Current implementation

The repository now supports building a corpus from local files:

- Markdown paper notes
- Text summaries
- JSON paper records
- PDF files when the optional parser dependency is available

## Recommended workflow

1. Collect papers or paper notes in `data/raw_papers/`.
2. Normalize them into a machine-readable corpus JSON.
3. Run the same baselines and multi-agent pipeline on the new corpus.
4. Expand the benchmark claim set as the corpus grows.

## Research benefit

This makes later experiments more credible because the dataset preparation process becomes explicit and repeatable.
