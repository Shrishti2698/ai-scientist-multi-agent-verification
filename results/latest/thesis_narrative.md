# Thesis Result Narrative



The multi-agent system achieves an accuracy of 0.917 on the current benchmark, outperforming the single-agent baseline (0.583) and the standard RAG baseline (0.667).

The critic-guided second pass changes overall accuracy by 0.084 relative to the no-loop ablation.

For the `critic` category specifically, accuracy changes from 0.5 to 1.0, suggesting whether the second pass helps on contradiction-heavy critic claims.

The remaining errors are concentrated in contradiction-sensitive retrieval and overclaim-style verification cases, which indicates that future improvements should focus on stronger counter-evidence retrieval and contradiction reasoning.
