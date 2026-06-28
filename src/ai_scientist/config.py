import os
from dataclasses import dataclass, field
from dataclasses import replace


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(slots=True)
class Settings:
    top_k_retrieval: int = 3
    second_pass_top_k: int = 5
    max_claims_per_question: int = 5
    min_query_relevance: float = 0.05
    # Minimum fraction of query content tokens a paper must contain to be retrieved.
    # Length-robust, unlike the Jaccard `min_query_relevance`.
    min_query_coverage: float = 0.2
    min_support_overlap: float = 0.18
    contradiction_overlap: float = 0.12
    strong_contradiction_score: float = 0.58
    confidence_floor: float = 0.2
    confidence_ceiling: float = 0.95
    critic_confidence_threshold: float = 0.6
    critic_min_evidence_count: int = 2
    enable_openai_llm: bool = False
    # When the retrieved papers are on-topic but the extracted claims are too thin to
    # answer the question, the Final Answer agent is allowed to complete the answer using
    # broadly established scientific knowledge. Kept on by default; the gate only opens
    # when claims are genuinely insufficient AND on-topic papers were retrieved.
    enable_adaptive_answer: bool = True
    # Live retrieval is opt-in so the default pipeline stays deterministic and
    # offline-testable. The app/API enable it explicitly for the hybrid demo.
    enable_live_retrieval: bool = False
    live_paper_quality_threshold: float = 0.3
    live_paper_quality_bonus: float = 0.12
    # Ranking bonuses enforce: user-uploaded papers > curated corpus > live API papers.
    uploaded_paper_quality_bonus: float = 0.30
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


    @classmethod
    def from_env(cls, **overrides) -> "Settings":
        """Build settings from environment variables, then apply explicit overrides.

        - OPENAI_API_KEY present -> enable the LLM verification/synthesis path.
        - OPENAI_MODEL / OPENAI_REASONING_EFFORT override the model defaults.
        - ENABLE_LIVE_RETRIEVAL toggles live PubMed/arXiv augmentation.
        """
        env_values: dict[str, object] = {
            "enable_openai_llm": bool(os.getenv("OPENAI_API_KEY")),
            "enable_live_retrieval": _env_bool("ENABLE_LIVE_RETRIEVAL", True),
        }
        if os.getenv("OPENAI_MODEL"):
            env_values["openai_model"] = os.environ["OPENAI_MODEL"]
        if os.getenv("OPENAI_REASONING_EFFORT"):
            env_values["openai_reasoning_effort"] = os.environ["OPENAI_REASONING_EFFORT"]
        env_values.update(overrides)
        return cls(**env_values)


def clone_settings(settings: Settings, **changes) -> Settings:
    return replace(settings, **changes)
