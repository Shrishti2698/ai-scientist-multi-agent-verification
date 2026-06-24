from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ai_scientist.agents.orchestrator import MultiAgentResearchSystem
from ai_scientist.bootstrap import load_environment
from ai_scientist.baselines import RagBaseline, SingleAgentBaseline
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository, load_benchmark_cases
from ai_scientist.evaluation import Evaluator

try:
    from fastapi import FastAPI
    from pydantic import BaseModel
except ModuleNotFoundError:
    FastAPI = None
    BaseModel = object


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"

load_environment()

settings = Settings.from_env()
corpus = CorpusRepository.from_path(DATA_DIR / "sample_corpus.json")
benchmark_cases = load_benchmark_cases(DATA_DIR / "benchmark_claims.json")
multi_agent_system = MultiAgentResearchSystem(settings=settings, corpus=corpus)
single_agent_baseline = SingleAgentBaseline(settings=settings, corpus=corpus)
rag_baseline = RagBaseline(settings=settings, corpus=corpus)
evaluator = Evaluator()


class _MissingDependencyApp:
    def __init__(self, message: str):
        self.title = "AI-Scientist (dependencies missing)"
        self.message = message

    async def __call__(self, scope, receive, send) -> None:
        body = self.message.encode("utf-8")
        headers = [(b"content-type", b"text/plain; charset=utf-8")]
        await send({"type": "http.response.start", "status": 503, "headers": headers})
        await send({"type": "http.response.body", "body": body})


if FastAPI is None:
    app = _MissingDependencyApp(
        "FastAPI is not installed. Install project dependencies before running the API."
    )
else:
    app = FastAPI(title="AI-Scientist")

    class QuestionRequest(BaseModel):
        question: str

    class ClaimRequest(BaseModel):
        claim: str

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/analyze")
    def analyze(request: QuestionRequest) -> dict:
        report = multi_agent_system.analyze_question(request.question)
        return {
            "question": report.question,
            "summary": report.summary,
            "markdown": report.markdown,
            "verified_claims": [asdict(item) for item in report.verified_claims],
            "critique_notes": [asdict(note) for note in report.critique_notes],
            "retrieved_papers": [asdict(paper) for paper in report.retrieved_papers],
        }

    @app.post("/baseline/single-agent")
    def single_agent_verify(request: ClaimRequest) -> dict:
        return asdict(single_agent_baseline.verify_claim(request.claim))

    @app.post("/baseline/rag")
    def rag_verify(request: ClaimRequest) -> dict:
        return asdict(rag_baseline.verify_claim(request.claim))

    @app.post("/verify-claim")
    def verify_claim(request: ClaimRequest) -> dict:
        return asdict(multi_agent_system.verify_claim(request.claim))

    @app.get("/evaluate")
    def evaluate() -> dict:
        summaries = [
            evaluator.evaluate_system("single_agent", single_agent_baseline, benchmark_cases),
            evaluator.evaluate_system("rag", rag_baseline, benchmark_cases),
            evaluator.evaluate_system("multi_agent", multi_agent_system, benchmark_cases),
        ]
        return {
            "summaries": [
                {
                    "system_name": summary.system_name,
                    "total_cases": summary.total_cases,
                    "accuracy": summary.accuracy,
                    "average_confidence": summary.average_confidence,
                    "average_evidence_count": summary.average_evidence_count,
                    "contradiction_recall": summary.contradiction_recall,
                    "category_accuracy": summary.category_accuracy,
                    "rows": [asdict(row) for row in summary.rows],
                }
                for summary in summaries
            ]
        }
