from __future__ import annotations

from ai_scientist.agents.claim_extraction import ClaimExtractionAgent
from ai_scientist.agents.critic import CriticAgent
from ai_scientist.agents.report import ReportGenerationAgent
from ai_scientist.agents.retrieval import RetrievalAgent
from ai_scientist.agents.synthesis import SynthesisAgent
from ai_scientist.agents.verification import VerificationAgent
from ai_scientist.config import Settings
from ai_scientist.corpus import CorpusRepository
from ai_scientist.models import ClaimAssessment, FinalReport, PaperDocument
from ai_scientist.scope import DomainScopeGuard


class MultiAgentResearchSystem:
    def __init__(self, settings: Settings, corpus: CorpusRepository, enable_second_pass: bool = True):
        self.settings = settings
        self.corpus = corpus
        self.enable_second_pass = enable_second_pass
        self.retrieval_agent = RetrievalAgent(corpus=corpus, settings=settings)
        self.claim_agent = ClaimExtractionAgent(settings=settings)
        self.verification_agent = VerificationAgent(corpus=corpus, settings=settings)
        self.critic_agent = CriticAgent(settings=settings)
        self.synthesis_agent = SynthesisAgent(settings=settings)
        self.report_agent = ReportGenerationAgent()
        self.scope_guard = DomainScopeGuard(settings=settings)

    def add_uploaded_papers(self, papers: list[PaperDocument]):
        """Add uploaded papers to the hybrid retrieval system."""
        self.retrieval_agent.add_uploaded_papers(papers)

    def analyze_question(self, question: str) -> FinalReport:
        scope = self.scope_guard.assess(question)
        if not scope.in_scope:
            return self.report_agent.build(
                question=question,
                summary=self.scope_guard.out_of_scope_message(scope),
                assessments=[],
                notes=[],
                papers=[],
                iteration_trace=[
                    "Analysis stopped before retrieval because the question is outside the research domain scope."
                ],
            )
        papers = self.retrieval_agent.retrieve(question)
        uploaded_papers = self.retrieval_agent.uploaded_papers  # Get uploaded papers count
        iteration_trace = [
            f"Pass 1 retrieved {len(papers)} paper(s) for the original question."
        ]
        if not papers:
            # More informative message for hybrid approach
            if uploaded_papers:
                summary = (
                    f"Found {len(uploaded_papers)} uploaded paper(s), but none were relevant to this question. "
                    "API retrieval also found no relevant papers. "
                    "Consider uploading more specific papers or reformulating your research question."
                )
            else:
                summary = (
                    "No uploaded papers available and API retrieval found no relevant papers for this question. "
                    "Try uploading relevant research papers or reformulating your research question to be more specific."
                )
            iteration_trace.append(f"Analysis stopped: No relevant papers found from uploads or APIs (uploaded: {len(uploaded_papers)}).")
            return self.report_agent.build(
                question=question,
                summary=summary,
                assessments=[],
                notes=[],
                papers=[],
                iteration_trace=iteration_trace,
            )
        claims = self.claim_agent.extract_claims(question=question, papers=papers)
        if not claims:
            summary = (
                "Relevant papers were retrieved, but no strong claim-level alignment was found for the question. "
                "The system returns insufficient evidence rather than overclaiming."
            )
            iteration_trace.append("No sufficiently aligned claims were extracted from the retrieved papers.")
            return self.report_agent.build(
                question=question,
                summary=summary,
                assessments=[],
                notes=[],
                papers=papers,
                iteration_trace=iteration_trace,
            )

        assessments = self._refine_assessments(claims=claims, initial_papers=papers, iteration_trace=iteration_trace)

        notes = self.critic_agent.critique(assessments)
        summary = self.synthesis_agent.synthesize(question=question, assessments=assessments, notes=notes)
        return self.report_agent.build(
            question=question,
            summary=summary,
            assessments=assessments,
            notes=notes,
            papers=papers,
            iteration_trace=iteration_trace,
        )

    def verify_claim(self, claim: str) -> ClaimAssessment:
        scope = self.scope_guard.assess(claim)
        if not scope.in_scope:
            return self.verification_agent.out_of_scope_assessment(
                claim,
                self.scope_guard.out_of_scope_message(scope),
            )
        papers = self.retrieval_agent.retrieve(claim)
        if not papers:
            return self.verification_agent.verify_claim(claim, candidate_papers=[])
        iteration_trace: list[str] = [f"Pass 1 retrieved {len(papers)} paper(s) for direct claim verification."]
        assessments = self._refine_assessments(claims=[claim], initial_papers=papers, iteration_trace=iteration_trace)
        return assessments[0]

    def _refine_assessments(
        self,
        claims,
        initial_papers: list[PaperDocument],
        iteration_trace: list[str],
    ) -> list[ClaimAssessment]:
        assessments = [
            self.verification_agent.verify_claim(claim, candidate_papers=initial_papers)
            for claim in claims
        ]
        decisions = self.critic_agent.identify_reverification_targets(assessments) if self.enable_second_pass else []
        if decisions:
            iteration_trace.append(f"Critic requested targeted re-verification for {len(decisions)} claim(s).")
            return self._run_second_pass(assessments, decisions, iteration_trace, initial_papers)
        if self.enable_second_pass:
            iteration_trace.append("Critic accepted first-pass evidence without targeted follow-up.")
        else:
            iteration_trace.append("Second-pass critic loop disabled for ablation.")
        return assessments

    def _run_second_pass(
        self,
        assessments: list[ClaimAssessment],
        decisions,
        iteration_trace: list[str],
        first_pass_papers: list[PaperDocument],
    ) -> list[ClaimAssessment]:
        updated: list[ClaimAssessment] = []
        decision_map = {item.claim_text: item for item in decisions}

        for assessment in assessments:
            decision = decision_map.get(assessment.claim.text)
            if decision is None:
                updated.append(assessment)
                continue

            targeted_papers = self.retrieval_agent.retrieve(
                decision.follow_up_query,
                top_k=self.settings.second_pass_top_k,
            )
            combined_papers = self._merge_papers(first_pass_papers, targeted_papers)
            refined = self.verification_agent.verify_claim(
                assessment.claim,
                candidate_papers=combined_papers,
                prefer_contradiction_resolution=True,
            )
            updated.append(refined)
            paper_titles = "; ".join(p.title for p in combined_papers)
            iteration_trace.append(
                f"Pass 2 revisited claim '{assessment.claim.text[:70]}' "
                f"(extracted from: '{assessment.claim.source_title}') "
                f"because {decision.reason}; "
                f"checked {len(combined_papers)} paper(s): {paper_titles}."
            )
        return updated

    def _merge_papers(
        self,
        left: list[PaperDocument],
        right: list[PaperDocument],
    ) -> list[PaperDocument]:
        merged: list[PaperDocument] = []
        seen: set[str] = set()
        for paper in left + right:
            if paper.paper_id in seen:
                continue
            merged.append(paper)
            seen.add(paper.paper_id)
        return merged
