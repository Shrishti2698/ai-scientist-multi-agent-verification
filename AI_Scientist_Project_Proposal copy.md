# AI-Scientist: A Multi-Agent Orchestrated Framework for Research Verification and Adaptive Reasoning

## Overview

This project aims to build an AI-Scientist system inspired by the PaperOrchestra paradigm. Instead of relying on a single LLM, the system uses an Orchestrator Agent to coordinate multiple specialized agents that collaboratively perform scientific reasoning, claim verification, evidence synthesis, and report generation.

The goal is to improve research verification, reduce hallucinations, and produce evidence-backed conclusions with confidence estimates.

---

## Problem Statement

Current LLM-based research assistants often:
- Generate answers without sufficient verification.
- Hallucinate facts or citations.
- Struggle with multi-step scientific reasoning.
- Do not explicitly critique or validate their own conclusions.

This project investigates whether a multi-agent orchestrated architecture can improve the reliability and quality of scientific reasoning compared to traditional single-agent and RAG-based approaches.

---

## Research Question

Can a multi-agent orchestrated framework improve scientific claim verification and adaptive reasoning compared to conventional single-agent or standard RAG systems?

---

## Objectives

1. Retrieve relevant scientific literature.
2. Extract important claims and hypotheses.
3. Verify claims using additional evidence sources.
4. Critique and validate findings.
5. Generate evidence-backed conclusions.
6. Provide confidence scores and traceable reasoning.
7. Evaluate the effectiveness of multi-agent orchestration.

---
# AI-Scientist: A Multi-Agent Orchestrated Framework for Research Verification and Adaptive Reasoning  (improving scientific research verification using a multi-agent architecture)

## High-Level Architecture

User Query
    |
    v
Orchestrator Agent
    |
    +---------------------------+
    |            |             |
    v            v             v
Literature   Claim         Verification
Retrieval    Extraction    Agent
Agent        Agent
    |            |             |
    +------------+-------------+
                 |
                 v
          Critic Agent
                 |
                 v
         Synthesis Agent
                 |
                 v
      Report Generation Agent
                 |
                 v
          Final Output

---
# psychology:-
How does social media use affect adolescents' positive and negative affect, depression, and stress markers?
Does social media use by depressed adolescents worsen family functioning and cohesion?
What clinical and physiological correlates are associated with problematic social media use in adolescents?


# medicine:-
Does metformin improve obesity, weight loss, and metabolic outcomes in type 2 diabetes?
How does BIAsp 30 plus metformin compare with BIAsp 30 monotherapy in cardiovascular risk and BMI profiles?
Is telemedical follow-up effective and accepted in epilepsy care and pediatric telemedicine centers?


# biology:-
Is CRISPR/Cas9 correction of the sickle mutation in human CD34+ cells a promising treatment for sickle cell disease?
What genome-editing tools are used to treat sickle cell disease, and what are their therapeutic limitations?
What do CRISPR translational reviews say about cancer treatment applications, ethical dilemmas, and the broader future of gene editing?


# CS/ AI:-
Does uncertainty detection improve dynamic retrieval-augmented generation when deciding whether to retrieve external knowledge?
How do THaMES and similar tools mitigate hallucination in large language models?
How do RAGPart, RAGMask, and query-level robustness studies improve retrieval-augmented generation reliability and defense against corpus poisoning?


# Uploaded Papers (High Confidence):
# Medicine Domain: 
Does metformin improve obesity, weight loss, and metabolic outcomes in type 2 diabetes?
How does BIAsp 30 plus metformin compare with BIAsp 30 monotherapy in cardiovascular risk and BMI profiles?
Is telemedical follow-up effective and accepted in epilepsy care and pediatric telemedicine centers?
(Expected: 85-95% confidence, clear evidence from abstracts)

# 🤖 AI/Computer Science Domain:
Does uncertainty detection improve dynamic retrieval-augmented generation when deciding whether to retrieve external knowledge?
How do THaMES and similar tools mitigate hallucination in large language models?
How do RAGPart, RAGMask, and query-level robustness studies improve retrieval-augmented generation reliability and defense against corpus poisoning?
(Expected: 80-90% confidence, well-supported claims)

#  🧬 Biology Domain:
Is CRISPR/Cas9 correction of the sickle mutation in human CD34+ cells a promising treatment for sickle cell disease?
What genome-editing tools are used to treat sickle cell disease, and what are their therapeutic limitations?
What do CRISPR translational reviews say about cancer treatment applications, ethical dilemmas, and the broader future of gene editing?
(Expected: 85-92% confidence, numerical evidence available)

# 🧠 Psychology Domain:
How does social media use affect adolescents' positive and negative affect, depression, and stress markers?
Does social media use by depressed adolescents worsen family functioning and cohesion?
What clinical and physiological correlates are associated with problematic social media use in adolescents?
(Expected: 80-88% confidence, clear statistical findings)

# Demo Script for Maximum Impact:
#  Does metformin show better weight management than insulin?  90
#  Do critic-guided verification loops improve claim checking?  85



# API Retrieval (Medium-High Confidence):
# 🏥 Medicine Domain (via PubMed API):
Does vitamin D supplementation reduce COVID-19 severity?
Is intermittent fasting effective for weight loss in obesity?
Do statins reduce cardiovascular mortality in elderly patients?
(Expected: 70-85% confidence, will find multiple PubMed papers)

# ⚛️ Physics Domain (via arXiv API):
Do quantum computers show advantage over classical computers for optimization problems?
Is room-temperature superconductivity achievable with high-pressure materials?
Do neural networks improve particle physics data analysis accuracy?
(Expected: 75-82% confidence, will retrieve arXiv preprints)

# 🧪 Chemistry Domain (via PubMed API):
Does green chemistry reduce environmental impact in pharmaceutical manufacturing?
Do metal-organic frameworks improve hydrogen storage efficiency?
Is machine learning effective for predicting drug molecular properties?
(Expected: 70-80% confidence, finds chemistry research papers)

# 🦠 Life Sciences Domain (via PubMed API):
Do mRNA vaccines provide longer immunity than traditional vaccines?
Is immunotherapy effective for treating melanoma cancer?
Do probiotics improve gut health in inflammatory bowel disease?
(Expected: 75-85% confidence, abundant medical literature)

# 💰 Finance Domain (via SSRN/Academic sources):
Does algorithmic trading outperform human traders in volatile markets?
Do ESG investments provide better long-term returns?
Is cryptocurrency adoption correlated with economic instability?
(Expected: 60-75% confidence, some papers found)




## Agent Responsibilities

### 1. Orchestrator Agent
- Central controller.
- Assigns tasks to other agents.
- Tracks workflow state.
- Decides when additional verification is needed.
- Determines stopping criteria.

### 2. Literature Retrieval Agent
- Retrieves relevant papers and documents.
- Performs semantic search over vector databases.
- Ranks relevant sources.

### 3. Claim Extraction Agent
- Extracts key claims, hypotheses, findings, and entities.
- Converts unstructured papers into structured knowledge.

### 4. Verification Agent
- Cross-checks extracted claims.
- Searches supporting or contradictory evidence.
- Validates facts across multiple sources.

### 5. Critic Agent
- Identifies weak reasoning.
- Detects unsupported claims.
- Highlights contradictions and missing evidence.

### 6. Synthesis Agent
- Combines validated evidence.
- Produces coherent scientific reasoning.

### 7. Report Generation Agent
- Creates final structured report.
- Includes sources and confidence estimates.
- Summarizes findings.

---

## Suggested Technology Stack

### Core Language
- Python

### Agent Framework
- LangGraph
- LangChain

### LLMs
- GPT-4o
- Claude
- Open-source alternatives (Llama models)

### Retrieval Layer
- RAG Pipeline
- Semantic Search

### Vector Database
- Qdrant
- ChromaDB

### Embeddings
- OpenAI Embeddings
- Sentence Transformers

### Backend
- FastAPI

### Frontend (Optional)
- Streamlit
- React

### Evaluation
- RAGAS
- Custom verification metrics

---

## Workflow

1. User submits a research question.
2. Orchestrator creates execution plan.
3. Literature Retrieval Agent collects sources.
4. Claim Extraction Agent identifies important claims.
5. Verification Agent validates claims.
6. Critic Agent reviews evidence quality.
7. Synthesis Agent integrates validated findings.
8. Report Generation Agent prepares final response.
9. Orchestrator evaluates completeness and either:
   - stops, or
   - launches another verification cycle.

---

## Experimental Evaluation

### Baselines
- Single LLM
- Standard RAG System

### Proposed System
- Multi-Agent Orchestrated AI-Scientist

### Metrics
- Claim Verification Accuracy
- Hallucination Rate
- Evidence Coverage
- Citation Quality
- Reasoning Consistency
- Response Completeness

---

## Expected Outcomes

- Improved factual reliability.
- Reduced hallucinations.
- Better scientific reasoning.
- Transparent evidence-backed outputs.
- Comparative analysis of multi-agent vs single-agent systems.

---

## Resume Title

AI-Scientist: A Multi-Agent Orchestrated Framework for Research Verification and Adaptive Reasoning

---

## Future Extensions

- Multi-modal scientific reasoning.
- Automatic hypothesis generation.
- Research gap identification.
- Scientific paper drafting assistance.
- Human-in-the-loop verification.
