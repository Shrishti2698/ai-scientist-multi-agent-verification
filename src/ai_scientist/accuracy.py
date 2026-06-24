from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict
import time

from ai_scientist.models import FinalReport, ClaimAssessment, PaperDocument


@dataclass
class AccuracyMetrics:
    """Overall accuracy metrics for the AI-Scientist system."""
    
    # Retrieval Accuracy
    retrieval_relevance_score: float = 0.0  # How relevant are retrieved papers
    retrieval_coverage_score: float = 0.0   # Did we find papers for the query
    
    # Claim Extraction Accuracy  
    claim_extraction_rate: float = 0.0      # % of papers that yielded claims
    claim_relevance_score: float = 0.0      # How relevant are extracted claims
    
    # Verification Accuracy
    evidence_quality_score: float = 0.0     # Quality of evidence matching
    confidence_calibration: float = 0.0     # How well calibrated are confidence scores
    
    # System Performance
    response_time_score: float = 0.0        # Speed performance score
    error_rate: float = 0.0                 # System failure rate
    
    # Overall Score
    overall_accuracy: float = 0.0


class AccuracyCalculator:
    """Calculate accuracy metrics for AI-Scientist system performance."""
    
    def __init__(self):
        self.query_history: List[Dict] = []
        
    def calculate_session_accuracy(self, reports: List[FinalReport]) -> AccuracyMetrics:
        """Calculate accuracy metrics for a session of queries."""
        if not reports:
            return AccuracyMetrics()
            
        metrics = AccuracyMetrics()
        
        # Calculate each component
        metrics.retrieval_relevance_score = self._calculate_retrieval_accuracy(reports)
        metrics.retrieval_coverage_score = self._calculate_coverage_accuracy(reports)
        metrics.claim_extraction_rate = self._calculate_extraction_accuracy(reports)
        metrics.claim_relevance_score = self._calculate_claim_relevance(reports)
        metrics.evidence_quality_score = self._calculate_evidence_quality(reports)
        metrics.confidence_calibration = self._calculate_confidence_calibration(reports)
        
        # Overall accuracy is weighted average
        metrics.overall_accuracy = (
            metrics.retrieval_relevance_score * 0.20 +
            metrics.retrieval_coverage_score * 0.15 +
            metrics.claim_extraction_rate * 0.15 +
            metrics.claim_relevance_score * 0.20 +
            metrics.evidence_quality_score * 0.20 +
            metrics.confidence_calibration * 0.10
        )
        
        return metrics
    
    def _calculate_retrieval_accuracy(self, reports: List[FinalReport]) -> float:
        """Calculate how relevant retrieved papers are to queries."""
        total_relevance = 0.0
        total_papers = 0
        
        for report in reports:
            query_terms = set(report.question.lower().split())
            
            for paper in report.retrieved_papers:
                # Calculate relevance based on term overlap
                paper_terms = set((paper.title + ' ' + paper.abstract).lower().split())
                overlap = len(query_terms & paper_terms) / max(len(query_terms), 1)
                total_relevance += overlap
                total_papers += 1
                
        return total_relevance / max(total_papers, 1)
    
    def _calculate_coverage_accuracy(self, reports: List[FinalReport]) -> float:
        """Calculate how well the system finds papers for queries."""
        successful_retrievals = 0
        
        for report in reports:
            if len(report.retrieved_papers) > 0:
                successful_retrievals += 1
                
        return successful_retrievals / len(reports)
    
    def _calculate_extraction_accuracy(self, reports: List[FinalReport]) -> float:
        """Calculate claim extraction success rate."""
        total_papers = 0
        papers_with_claims = 0
        
        for report in reports:
            total_papers += len(report.retrieved_papers)
            
            # Count unique source papers that contributed claims
            source_papers = set()
            for claim in report.verified_claims:
                source_papers.add(claim.claim.source_paper_id)
            papers_with_claims += len(source_papers)
            
        return papers_with_claims / max(total_papers, 1)
    
    def _calculate_claim_relevance(self, reports: List[FinalReport]) -> float:
        """Calculate how relevant extracted claims are to the query."""
        total_relevance = 0.0
        total_claims = 0
        
        for report in reports:
            query_terms = set(report.question.lower().split())
            
            for claim_assessment in report.verified_claims:
                claim_terms = set(claim_assessment.claim.text.lower().split())
                overlap = len(query_terms & claim_terms) / max(len(query_terms), 1)
                total_relevance += overlap
                total_claims += 1
                
        return total_relevance / max(total_claims, 1)
    
    def _calculate_evidence_quality(self, reports: List[FinalReport]) -> float:
        """Calculate quality of evidence matching."""
        total_evidence_score = 0.0
        total_claims = 0
        
        for report in reports:
            for claim_assessment in report.verified_claims:
                total_claims += 1
                
                if claim_assessment.evidence:
                    # Average overlap score of evidence
                    avg_overlap = sum(e.overlap_score for e in claim_assessment.evidence) / len(claim_assessment.evidence)
                    total_evidence_score += avg_overlap
                else:
                    # No evidence found
                    total_evidence_score += 0.0
                    
        return total_evidence_score / max(total_claims, 1)
    
    def _calculate_confidence_calibration(self, reports: List[FinalReport]) -> float:
        """Calculate how well confidence scores match evidence quality."""
        calibration_scores = []
        
        for report in reports:
            for claim_assessment in report.verified_claims:
                # Compare confidence to evidence strength
                evidence_strength = 0.0
                
                if claim_assessment.evidence:
                    evidence_strength = sum(e.overlap_score for e in claim_assessment.evidence) / len(claim_assessment.evidence)
                
                # Good calibration means confidence aligns with evidence
                expected_confidence = min(0.95, 0.2 + (evidence_strength * 0.7))
                actual_confidence = claim_assessment.confidence
                
                calibration_error = abs(expected_confidence - actual_confidence)
                calibration_score = max(0.0, 1.0 - calibration_error)
                calibration_scores.append(calibration_score)
        
        return sum(calibration_scores) / max(len(calibration_scores), 1)
    
    def log_query_performance(self, query: str, report: FinalReport, response_time: float):
        """Log individual query performance for tracking."""
        self.query_history.append({
            'query': query,
            'papers_retrieved': len(report.retrieved_papers),
            'claims_found': len(report.verified_claims),
            'has_supported_claims': any(c.verdict == 'supported' for c in report.verified_claims),
            'avg_confidence': sum(c.confidence for c in report.verified_claims) / max(len(report.verified_claims), 1),
            'response_time': response_time,
            'timestamp': time.time()
        })
    
    def get_accuracy_summary(self) -> Dict[str, float]:
        """Get simple accuracy summary for display."""
        if not self.query_history:
            return {}
            
        recent_queries = self.query_history[-10:]  # Last 10 queries
        
        return {
            'retrieval_success_rate': sum(1 for q in recent_queries if q['papers_retrieved'] > 0) / len(recent_queries),
            'claim_extraction_rate': sum(1 for q in recent_queries if q['claims_found'] > 0) / len(recent_queries),
            'average_confidence': sum(q['avg_confidence'] for q in recent_queries) / len(recent_queries),
            'average_response_time': sum(q['response_time'] for q in recent_queries) / len(recent_queries),
        }