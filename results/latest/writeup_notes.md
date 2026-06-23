# Thesis Writeup Notes

## Methodology Summary
- Compare `single_agent`, `rag`, `multi_agent_no_critic_loop`, and `multi_agent` on the same benchmark.
- Use structured claims, evidence-aware verification, and critic-guided re-verification.
- Report overall accuracy, contradiction recall, evidence count, and category-wise accuracy.

## Result Discussion Prompts
- Explain why the multi-agent systems outperform the simpler baselines on contradiction-heavy retrieval cases.
- Discuss why the critic loop may or may not improve over the no-loop ablation on the current corpus.
- Highlight that failure analysis exposes remaining weaknesses in critic-oriented contradiction cases.
