# Phase 12: Iterative Critic-Guided Verification

## Goal

Make the orchestrator adaptive by allowing the critic to trigger a second verification pass for weak claims.

## Why this matters

This is one of the most important shifts from a simple pipeline to a research-worthy multi-agent system. The orchestration is no longer only sequential. It can react to uncertainty and ask for more evidence.

## Current implementation

The system now performs:

1. first-pass retrieval and verification,
2. critic review of confidence and evidence strength,
3. targeted follow-up retrieval for weak claims,
4. second-pass verification with expanded candidate papers.

## Research benefit

This directly supports your proposal’s claim about adaptive reasoning and iterative verification.

## Current limitation

The second pass is still heuristic and retrieval-guided, not LLM-planned. That is acceptable for the MVP, and it gives us a clean upgrade path for later experiments.
