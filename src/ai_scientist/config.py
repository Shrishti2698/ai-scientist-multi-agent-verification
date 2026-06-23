from dataclasses import dataclass, field
from dataclasses import replace


@dataclass(slots=True)
class Settings:
    top_k_retrieval: int = 3
    second_pass_top_k: int = 5
    max_claims_per_question: int = 5
    min_query_relevance: float = 0.05
    min_support_overlap: float = 0.18
    contradiction_overlap: float = 0.12
    strong_contradiction_score: float = 0.58
    confidence_floor: float = 0.2
    confidence_ceiling: float = 0.95
    critic_confidence_threshold: float = 0.6
    critic_min_evidence_count: int = 2
    enable_openai_llm: bool = False
    openai_model: str = "gpt-5.5"
    openai_reasoning_effort: str = "medium"
    openai_max_output_tokens: int = 800
    in_scope_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "ai",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "neural",
            "language model",
            "large language model",
            "llm",
            "nlp",
            "natural language processing",
            "computer vision",
            "reinforcement learning",
            "rag",
            "retrieval",
            "retrieval-augmented",
            "hallucination",
            "prompt",
            "prompting",
            "agent",
            "agentic",
            "multi-agent",
            "critic",
            "verification",
            "scientific verification",
            "claim extraction",
            "benchmark",
            "dataset",
            "training",
            "inference",
            "transformer",
            "algorithm",
            "computer science",
            "software",
            "program",
            "compiler",
            "database",
            "operating system",
            "cybersecurity",
            "distributed system",
            "knowledge graph",
            "scientific paper",
            "research assistant",
        )
    )
    out_of_scope_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "medical",
            "medicine",
            "clinical",
            "patient",
            "disease",
            "diabetes",
            "cancer",
            "hospital",
            "drug",
            "treatment",
            "therapy",
            "surgery",
            "law",
            "legal",
            "judicial",
            "justice",
            "court",
            "judge",
            "lawyer",
            "lawyers",
            "attorney",
            "attorneys",
            "litigation",
            "crime",
            "criminal",
            "sentencing",
            "policy",
            "regulation",
            "regulatory",
            "contract",
            "constitution",
            "biology",
            "genetics",
            "protein",
            "chemistry",
            "molecule",
            "physics",
            "quantum",
            "finance",
            "stock",
            "market",
            "economics",
        )
    )
    positive_cues: tuple[str, ...] = field(
        default_factory=lambda: (
            "improve",
            "improves",
            "improved",
            "reduce",
            "reduces",
            "reduced",
            "increase",
            "increases",
            "outperform",
            "outperforms",
            "achieve",
            "achieves",
            "show",
            "shows",
            "demonstrate",
            "demonstrates",
            "mitigate",
            "mitigates",
            "enhance",
            "enhances",
        )
    )
    contradiction_terms: tuple[str, ...] = field(
        default_factory=lambda: (
            "not",
            "no",
            "fails",
            "fail",
            "insufficient",
            "unlikely",
            "little effect",
            "does not",
            "do not",
            "cannot",
            "without",
            "limited",
            "however",
            "but",
            "despite",
        )
    )
    contradiction_claim_cues: tuple[str, ...] = field(
        default_factory=lambda: (
            "sufficient",
            "always",
            "eliminate",
            "all factual errors",
            "little effect",
            "regardless",
        )
    )
    overgeneralization_cues: tuple[str, ...] = field(
        default_factory=lambda: (
            "this corpus",
            "every ",
            "prove",
            "proves",
        )
    )


def clone_settings(settings: Settings, **changes) -> Settings:
    return replace(settings, **changes)
