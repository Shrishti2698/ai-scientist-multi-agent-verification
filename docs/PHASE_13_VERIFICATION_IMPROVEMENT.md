# Phase 13: Verification Improvement

## Goal

Improve claim verification quality so the research comparison reflects reasoning improvements, not only system structure.

## What changed

The verifier now uses stronger evidence scoring based on:

- lexical overlap,
- focus-term overlap,
- claim-term coverage,
- source-paper preference,
- and better negation handling.

## Why this matters

This reduces false contradictions caused by naive token matching and makes the verification stage more faithful to scientific claims that include nuance or limitations.

## Current outcome

On the current offline benchmark:

- `single_agent` accuracy is `0.5`
- `rag` accuracy is `0.667`
- `multi_agent` accuracy is `0.833`

## Remaining limitation

The verifier is still heuristic rather than model-based. That is fine for the MVP, but a later thesis stage should compare this rule-based verifier against an LLM-assisted or NLI-style verifier.
