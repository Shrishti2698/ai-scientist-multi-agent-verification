# Phase 14: Ablation Studies

## Goal

Measure whether the critic-guided second pass actually improves the system, instead of assuming that more orchestration is always better.

## Current implementation

The experiment runner now compares:

- `single_agent`
- `rag`
- `multi_agent_no_critic_loop`
- `multi_agent`

## Why this matters

This is one of the clearest places where your research contribution becomes visible. If the second pass helps, you can argue that adaptive orchestration adds value. If it does not help, that is also a valid research finding.

## Expected use in thesis

This ablation should appear in:

- experiment tables,
- result discussion,
- and the section on the usefulness of the critic agent.
