# Failure Analysis

## single_agent
- Accuracy: 0.583
- Incorrect cases: 5
- Error categories: retrieval=2, verification=1, generalization=1, critic=1
- Verdict confusions: contradicted -> supported=2, contradicted -> insufficient_evidence=2, insufficient_evidence -> supported=1

### Misclassified Cases
- C2 [verification]
  Claim: Direct prompting alone is sufficient for scientific verification.
  Expected: `contradicted` | Predicted: `supported` | Confidence: `0.6`
- C4 [retrieval]
  Claim: Retrieval always reduces hallucination, regardless of retriever quality.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
- C6 [generalization]
  Claim: This corpus proves that agentic systems solve all factual errors.
  Expected: `insufficient_evidence` | Predicted: `supported` | Confidence: `0.6`
- C9 [critic]
  Claim: Critic stages eliminate all factual errors in research assistants.
  Expected: `contradicted` | Predicted: `supported` | Confidence: `0.686`
- C11 [retrieval]
  Claim: Retrieval quality has little effect on hallucination behavior in RAG systems.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`

## rag
- Accuracy: 0.667
- Incorrect cases: 4
- Error categories: retrieval=2, verification=1, critic=1
- Verdict confusions: contradicted -> insufficient_evidence=4

### Misclassified Cases
- C2 [verification]
  Claim: Direct prompting alone is sufficient for scientific verification.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
- C4 [retrieval]
  Claim: Retrieval always reduces hallucination, regardless of retriever quality.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
- C9 [critic]
  Claim: Critic stages eliminate all factual errors in research assistants.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
- C11 [retrieval]
  Claim: Retrieval quality has little effect on hallucination behavior in RAG systems.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`

## multi_agent_no_critic_loop
- Accuracy: 0.833
- Incorrect cases: 2
- Error categories: critic=1, retrieval=1
- Verdict confusions: contradicted -> insufficient_evidence=2

### Misclassified Cases
- C9 [critic]
  Claim: Critic stages eliminate all factual errors in research assistants.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
- C11 [retrieval]
  Claim: Retrieval quality has little effect on hallucination behavior in RAG systems.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`

## multi_agent
- Accuracy: 0.917
- Incorrect cases: 1
- Error categories: retrieval=1
- Verdict confusions: contradicted -> insufficient_evidence=1

### Misclassified Cases
- C11 [retrieval]
  Claim: Retrieval quality has little effect on hallucination behavior in RAG systems.
  Expected: `contradicted` | Predicted: `insufficient_evidence` | Confidence: `0.2`
