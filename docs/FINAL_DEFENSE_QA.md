# Final Defense Q&A

## Why is this a research project and not just software development?

- The project compares `single_agent`, `rag`, `multi_agent_no_critic_loop`, and `multi_agent`.
- It evaluates whether orchestration improves claim verification and contradiction handling.
- It includes ablation studies, category-wise analysis, and failure analysis.

## What is the main contribution?

- A domain-focused multi-agent framework for AI/CS literature verification.
- A critic-guided re-verification loop that improves contradiction-heavy benchmark performance.
- A reproducible benchmark and evaluation workflow with thesis-ready artifacts.

## Why did you choose AI/CS literature instead of all scientific domains?

- It keeps scope realistic for an MTech project.
- It makes dataset collection and evaluation tractable.
- It avoids overclaiming generalization beyond the available corpus.

## Why is the critic loop important?

- It makes the system adaptive instead of purely sequential.
- It improves the current benchmark from `0.833` to `0.917` over the no-loop multi-agent ablation.
- It especially helps on contradiction-heavy critic claims.

## What are the current limitations?

- The verifier is still heuristic rather than model-based.
- The benchmark is still relatively small and domain-focused.
- Live literature fetching depends on external network conditions and source availability.

## What would be the next research extension?

- Larger real-world corpora with live fetched papers.
- Model-assisted or NLI-style verification.
- More rigorous contradiction-aware retrieval.
- Human evaluation and expert annotation.
