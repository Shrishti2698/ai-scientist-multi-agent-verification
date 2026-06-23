# Methodology Chapter Outline

## 1. Problem Definition
- Define scientific claim verification over AI and computer science literature.
- Motivate the need for verification-aware research assistants.

## 2. System Design
- Describe the orchestrator and each specialized agent.
- Explain the baseline systems and why they were selected.

## 3. Data and Benchmark
- Describe the curated corpus and benchmark claims.
- Explain category labels, difficulty labels, and evaluation assumptions.

## 4. Experimental Setup
- Report the benchmark protocol for `single_agent`, `rag`, `multi_agent_no_critic_loop`, and `multi_agent`.
- Explain the critic-loop ablation and evaluation metrics.

## 5. Evaluation Metrics
- Accuracy
- Contradiction recall
- Average evidence count
- Category-wise accuracy

## 6. Failure Analysis
- Group errors by contradiction handling, retrieval failures, and overclaim-style generalization.

## 7. Threats to Validity
- Limited benchmark size
- Heuristic verifier bias
- Static offline corpus limitations
