from __future__ import annotations

from dataclasses import dataclass, field


Verdict = str


@dataclass(slots=True)
class PaperDocument:
    paper_id: str
    title: str
    abstract: str
    year: int
    authors: list[str]
    topics: list[str]


@dataclass(slots=True)
class StructuredClaim:
    text: str
    claim_type: str
    source_paper_id: str
    source_title: str
    source_sentence: str
    focus_terms: list[str] = field(default_factory=list)


@dataclass(slots=True)
class EvidenceSnippet:
    paper_id: str
    title: str
    sentence: str
    overlap_score: float


@dataclass(slots=True)
class ClaimAssessment:
    claim: StructuredClaim
    verdict: Verdict
    confidence: float
    evidence: list[EvidenceSnippet] = field(default_factory=list)
    rationale: str = ""


@dataclass(slots=True)
class CritiqueNote:
    claim: str
    severity: str
    message: str


@dataclass(slots=True)
class FinalReport:
    question: str
    summary: str
    verified_claims: list[ClaimAssessment]
    critique_notes: list[CritiqueNote]
    retrieved_papers: list[PaperDocument]
    markdown: str
    iteration_trace: list[str] = field(default_factory=list)
    # Direct, user-facing answer to the question, composed by the Final Answer agent
    # from the verified claims (falls back to the claims summary when absent).
    final_answer: str = ""


@dataclass(slots=True)
class BenchmarkCase:
    case_id: str
    claim: str
    expected_verdict: Verdict
    query_hint: str
    category: str = "general"
    difficulty: str = "medium"
    source_note: str = ""


@dataclass(slots=True)
class EvaluationRow:
    system_name: str
    case_id: str
    predicted_verdict: Verdict
    expected_verdict: Verdict
    confidence: float
    evidence_count: int
    is_correct: bool


@dataclass(slots=True)
class EvaluationSummary:
    system_name: str
    total_cases: int
    accuracy: float
    average_confidence: float
    average_evidence_count: float
    contradiction_recall: float
    rows: list[EvaluationRow]
    category_accuracy: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class IterationDecision:
    claim_text: str
    reason: str
    follow_up_query: str
