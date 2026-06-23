from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, Field

try:
    from openai import OpenAI
except ModuleNotFoundError:  # pragma: no cover - fallback for environments without the package
    OpenAI = None

from ai_scientist.config import Settings
from ai_scientist.models import ClaimAssessment, CritiqueNote, EvidenceSnippet, PaperDocument, StructuredClaim


class VerificationRefinement(BaseModel):
    verdict: Literal["supported", "contradicted", "insufficient_evidence"]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    evidence_indices: list[int] = Field(default_factory=list)


class SummaryDraft(BaseModel):
    summary: str


class OpenAIResearchLLM:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.model = settings.openai_model
        self.reasoning_effort = settings.openai_reasoning_effort
        self.client = self._build_client()

    @classmethod
    def from_settings(cls, settings: Settings) -> "OpenAIResearchLLM":
        return cls(settings=settings)

    @property
    def available(self) -> bool:
        return self.settings.enable_openai_llm and self.client is not None

    def refine_verification(
        self,
        claim: StructuredClaim,
        preliminary: ClaimAssessment,
        supporting: list[EvidenceSnippet],
        contradictory: list[EvidenceSnippet],
    ) -> ClaimAssessment | None:
        if not self.available:
            return None

        evidence_lines = self._format_evidence(supporting, contradictory)
        if not evidence_lines:
            return None

        prompt = (
            "You are a rigorous verifier for AI and computer science research claims.\n"
            "Use only the provided evidence snippets.\n"
            "Keep the final verdict aligned to the evidence.\n"
            "If evidence is mixed, prefer contradicted over supported when strong counterevidence exists.\n"
            "If the evidence is too thin or unrelated, choose insufficient_evidence.\n"
            "Return concise reasoning and select the most relevant evidence indices."
        )
        user_input = (
            f"CLAIM:\n{claim.text}\n\n"
            f"PRELIMINARY VERDICT:\n{preliminary.verdict}\n"
            f"PRELIMINARY CONFIDENCE:\n{preliminary.confidence}\n\n"
            f"EVIDENCE:\n{evidence_lines}"
        )
        parsed = self._parse_response(
            prompt,
            user_input,
            VerificationRefinement,
        )
        if parsed is None:
            return None

        selected_evidence = self._select_evidence(parsed.evidence_indices, supporting, contradictory)
        confidence = self._calibrate_confidence(parsed.confidence, parsed.verdict, len(selected_evidence))
        return ClaimAssessment(
            claim=claim,
            verdict=parsed.verdict,
            confidence=confidence,
            evidence=selected_evidence,
            rationale=parsed.rationale,
        )

    def rewrite_summary(
        self,
        question: str,
        assessments: list[ClaimAssessment],
        notes: list[CritiqueNote],
    ) -> str | None:
        if not self.available:
            return None

        if not assessments:
            return None

        lines = [f"QUESTION: {question}", "", "CLAIMS:"]
        for index, item in enumerate(assessments, start=1):
            lines.append(
                f"{index}. {item.claim.text} | verdict={item.verdict} | confidence={item.confidence} | "
                f"source={item.claim.source_title}"
            )
        if notes:
            lines.append("")
            lines.append("CRITIQUE:")
            for note in notes:
                lines.append(f"- {note.severity}: {note.message}")

        prompt = (
            "You are writing the executive summary for an AI/CS research verification report.\n"
            "State the overall finding clearly in 2 to 4 sentences.\n"
            "Be precise, research-oriented, and do not overclaim.\n"
            "Mention that evidence is grounded in the current corpus and note uncertainty when relevant."
        )
        parsed = self._parse_response(prompt, "\n".join(lines), SummaryDraft)
        if parsed is None:
            return None
        return parsed.summary.strip()

    def _build_client(self):
        if OpenAI is None:
            return None
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)

    def _parse_response(self, instructions: str, input_text: str, response_model):
        try:
            response = self.client.responses.parse(
                model=self.model,
                instructions=instructions,
                input=input_text,
                reasoning={"effort": self.reasoning_effort},
                max_output_tokens=self.settings.openai_max_output_tokens,
                text_format=response_model,
            )
        except Exception:
            return None
        return getattr(response, "output_parsed", None)

    def _format_evidence(
        self,
        supporting: list[EvidenceSnippet],
        contradictory: list[EvidenceSnippet],
    ) -> str:
        indexed: list[str] = []
        counter = 1
        for label, snippets in (("supporting", supporting), ("contradictory", contradictory)):
            for snippet in snippets[:3]:
                indexed.append(
                    f"[{counter}] {label} | {snippet.title} | overlap={snippet.overlap_score} | {snippet.sentence}"
                )
                counter += 1
        return "\n".join(indexed)

    def _select_evidence(
        self,
        indices: list[int],
        supporting: list[EvidenceSnippet],
        contradictory: list[EvidenceSnippet],
    ) -> list[EvidenceSnippet]:
        ordered = supporting[:3] + contradictory[:3]
        selected: list[EvidenceSnippet] = []
        for index in indices:
            if 1 <= index <= len(ordered):
                selected.append(ordered[index - 1])
        return selected[:3]

    def _calibrate_confidence(self, raw_confidence: float, verdict: str, evidence_count: int) -> float:
        raw_confidence = max(0.0, min(1.0, raw_confidence))
        if verdict == "insufficient_evidence":
            base = 0.58
            spread = 0.18
            return round(min(0.78, base + (raw_confidence * spread)), 3)

        base = 0.78 if evidence_count >= 2 else 0.74
        spread = 0.16
        return round(min(0.95, base + (raw_confidence * spread) + (0.02 * min(evidence_count, 3))), 3)
