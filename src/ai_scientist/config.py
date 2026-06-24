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
    enable_live_retrieval: bool = True
    live_paper_quality_threshold: float = 0.3
    local_paper_quality_bonus: float = 0.15
    openai_model: str = "gpt-5.5"
    openai_reasoning_effort: str = "medium"
    openai_max_output_tokens: int = 800
    research_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "research",
            "study",
            "analysis",
            "experiment",
            "investigation",
            "methodology",
            "findings",
            "results",
            "hypothesis",
            "theory",
            "model",
            "framework",
            "approach",
            "technique",
            "method",
            "algorithm",
            "evaluation",
            "assessment",
            "comparison",
            "performance",
            "effectiveness",
            "efficacy",
            "impact",
            "correlation",
            "causation",
            "statistical",
            "empirical",
            "quantitative",
            "qualitative",
            "systematic",
            "meta-analysis",
            "literature review",
            "peer review",
            "publication",
            "journal",
            "conference",
            "academic",
            "scholarly",
            "scientific",
            "evidence",
            "data",
            "dataset",
            "sample",
            "population",
            "survey",
            "interview",
            "observation",
            "case study",
            "longitudinal",
            "cross-sectional",
            "randomized",
            "controlled",
            "trial",
            "significance",
            "p-value",
            "confidence interval",
            "regression",
            "correlation",
            "variance",
            "standard deviation",
            "mean",
            "median",
            "distribution",
        )
    )
    non_research_keywords: tuple[str, ...] = field(
        default_factory=lambda: (
            "shopping",
            "recipe",
            "cooking",
            "entertainment",
            "movie",
            "game",
            "sports",
            "weather",
            "news",
            "gossip",
            "celebrity",
            "fashion",
            "travel",
            "vacation",
            "personal advice",
            "relationship",
            "dating",
            "joke",
            "funny",
            "meme",
            "chat",
            "conversation",
            "how to fix",
            "repair",
            "tutorial",
            "diy",
            "price",
            "buy",
            "sell",
            "product review",
            "recommendation",
            "best phone",
            "best laptop",
            "which car",
            "opinion",
            "what do you think",
            "personal preference",
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
