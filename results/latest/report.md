# Experiment Report

## System Summaries
### single_agent
- Total cases: 12
- Accuracy: 0.583
- Average confidence: 0.604
- Average evidence count: 0.0
- Contradiction recall: 0.0
- Category accuracy: critic=0.5, extraction=1.0, generalization=0.5, multi_agent=1.0, retrieval=0.333, verification=0.5

### rag
- Total cases: 12
- Accuracy: 0.667
- Average confidence: 0.531
- Average evidence count: 0.0
- Contradiction recall: 0.0
- Category accuracy: critic=0.5, extraction=1.0, generalization=1.0, multi_agent=1.0, retrieval=0.333, verification=0.5

### multi_agent_no_critic_loop
- Total cases: 12
- Accuracy: 0.833
- Average confidence: 0.577
- Average evidence count: 1.0
- Contradiction recall: 0.5
- Category accuracy: critic=0.5, extraction=1.0, generalization=1.0, multi_agent=1.0, retrieval=0.667, verification=1.0

### multi_agent
- Total cases: 12
- Accuracy: 0.917
- Average confidence: 0.609
- Average evidence count: 1.083
- Contradiction recall: 0.75
- Category accuracy: critic=1.0, extraction=1.0, generalization=1.0, multi_agent=1.0, retrieval=0.667, verification=1.0

## Headline Finding
The best accuracy in this run came from `multi_agent` with a score of `0.917`.

## Critic Loop Ablation
The critic-guided second pass changes multi-agent accuracy by `0.084` compared to the no-loop ablation.

## Notes
These results are from the current offline benchmark and should be treated as early-stage research signals.
