# LLM Upgrade Plan

## Objective

Move the project from a heuristic prototype to a hybrid OpenAI-backed research system without changing the current Streamlit layout.

## Phase 1: Environment And Bootstrapping

- Load `.env` automatically at startup
- Read `OPENAI_API_KEY` from the project root
- Add OpenAI SDK and dotenv dependencies

## Phase 2: Model Integration

- Use `gpt-5.5` as the default OpenAI model
- Add structured outputs for verification and summary tasks
- Keep heuristic fallbacks for offline runs and tests

## Phase 3: Agent Upgrade

- Use the LLM for claim verification
- Use the LLM for final synthesis
- Preserve the critic loop and baseline systems for research comparison

## Phase 4: Calibration

- Keep confidence values variable instead of fixed
- Avoid overly low confidence for supported in-scope claims
- Keep insufficient evidence visibly uncertain

## Phase 5: Validation

- Run the existing unit tests
- Check AI/CS questions and out-of-scope rejection
- Compare LLM mode against the heuristic baselines

## Phase 6: Demo Readiness

- Keep the Streamlit layout unchanged
- Add only small status or explanation text if needed
- Make the project easy to explain in a thesis defense

## Current State

- Scope guard is already in place
- Heuristic baselines still work
- The multi-agent system now has an OpenAI-backed verification and synthesis path when `OPENAI_API_KEY` is available
- The project should be run with `py -3` on Windows if `python` points to the MSYS runtime
