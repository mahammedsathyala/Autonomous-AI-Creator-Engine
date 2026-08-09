from typing import Dict, Any, Tuple
from aegis.config import settings
from aegis.llm_client import llm_client

class TopicScorer:
    """
    Deterministic 5-Dimensional Evaluator:
    - LLM or rule engine outputs 5 dimension scores (0-100 each).
    - Python computes deterministic weighted average score.
    - Applies strict decision thresholds:
        - score >= 75.0 -> ACCEPTED (Publish)
        - score >= 60.0 -> HOLD (Hold for further verification)
        - score < 60.0  -> REJECTED
    """
    def score_topic(self, title: str, summary: str, domain: str) -> Tuple[str, float, Dict[str, float], str]:
        dims = llm_client.evaluate_topic_dimensions(title, summary, domain)

        # Compute deterministic weighted score
        final_score = (
            (dims["security_impact"] * settings.WEIGHT_SECURITY_IMPACT) +
            (dims["novelty"] * settings.WEIGHT_NOVELTY) +
            (dims["evidence_quality"] * settings.WEIGHT_EVIDENCE_QUALITY) +
            (dims["ai_relevance"] * settings.WEIGHT_AI_RELEVANCE) +
            (dims["research_value"] * settings.WEIGHT_RESEARCH_VALUE)
        )
        final_score = round(final_score, 1)

        # Decision threshold check
        if final_score >= settings.PUBLISH_THRESHOLD:
            status = "ACCEPTED"
            reason = (
                f"ACCEPTED for Publication: Score ({final_score}/100) exceeds publish threshold ({settings.PUBLISH_THRESHOLD}). "
                f"Breakdown: Security Impact: {dims['security_impact']}, Novelty: {dims['novelty']}, Evidence Quality: {dims['evidence_quality']}, AI Relevance: {dims['ai_relevance']}."
            )
        elif final_score >= settings.HOLD_THRESHOLD:
            status = "HOLD"
            reason = (
                f"HELD for Further Evidence: Score ({final_score}/100) between hold threshold ({settings.HOLD_THRESHOLD}) and publish threshold ({settings.PUBLISH_THRESHOLD})."
            )
        else:
            status = "REJECTED"
            reason = (
                f"REJECTED by Editorial Standards: Score ({final_score}/100) below quality threshold ({settings.HOLD_THRESHOLD}). "
                f"Lacks sufficient technical depth, novelty, or security relevance."
            )

        return status, final_score, dims, reason

topic_scorer = TopicScorer()
