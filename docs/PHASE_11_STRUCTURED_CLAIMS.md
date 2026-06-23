# Phase 11: Structured Claim Representation

## Goal

Upgrade the system from sentence-level extraction to structured scientific claims that can support stronger verification and reporting.

## Why this matters

If the system only passes raw sentences between agents, the pipeline looks more like text processing than scientific reasoning. Structured claims make the agent workflow easier to inspect, evaluate, and defend in a research presentation.

## Current implementation

Each extracted claim now includes:

- claim text,
- claim type,
- source paper identity,
- source sentence,
- and focus terms linked to the user question.

## Research benefit

This improves:

- interpretability of intermediate reasoning,
- traceability from output back to source text,
- and future support for claim-level evaluation and ablation studies.

## Next extension

The next natural upgrade is to add claim attributes such as:

- entities,
- method names,
- datasets,
- and numerical outcomes.
