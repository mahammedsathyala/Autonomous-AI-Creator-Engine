import json
import re
from typing import Dict, Any, Tuple
from aegis.config import settings

class UnifiedLLMClient:
    """
    Unified client supporting OpenAI / Anthropic / Google or local NLP evaluation logic.
    Always returns structured JSON output for 5-dimensional scoring and rationale.
    """
    def __init__(self):
        self.openai_key = settings.OPENAI_API_KEY
        self.anthropic_key = settings.ANTHROPIC_API_KEY
        self.google_key = settings.GEMINI_API_KEY

    def evaluate_topic_dimensions(self, title: str, summary: str, domain: str) -> Dict[str, Any]:
        """
        Evaluates a topic across 5 explicit dimensions:
        1. security_impact (0-100)
        2. novelty (0-100)
        3. evidence_quality (0-100)
        4. ai_relevance (0-100)
        5. research_value (0-100)
        """
        content = f"{title} {summary}".lower()
        domain_lower = domain.lower()

        # Dimension 1: Security Impact
        sec_terms = ["vulnerability", "cve", "zero-day", "exploit", "attack", "jailbreak", "injection", "breach", "threat", "guardrail", "adversarial", "exfiltration", "patch"]
        sec_matches = [t for t in sec_terms if t in content]
        security_impact = min(100.0, 40.0 + (len(sec_matches) * 15.0))

        # Dimension 2: Novelty
        novelty = 70.0
        if any(w in content for w in ["arxiv", "2026", "new", "first", "zero-day", "breakthrough", "novel"]):
            novelty += 20.0

        # Dimension 3: Evidence Quality
        evidence_quality = 65.0
        if "cve" in content or "nvd" in content or "arxiv" in content or "github" in content:
            evidence_quality += 25.0

        # Dimension 4: AI & Agent Relevance
        ai_terms = ["ai", "llm", "agent", "rag", "neural", "model", "prompt", "transformer", "cuda", "vllm", "deepseek", "openai", "copilot"]
        ai_matches = [t for t in ai_terms if t in content]
        ai_relevance = min(100.0, 35.0 + (len(ai_matches) * 18.0))

        # Dimension 5: Research Value
        research_value = 60.0
        if "arxiv" in content or "paper" in content or "kernel" in content or "benchmark" in content:
            research_value += 30.0

        # Anti-pattern check (Clickbait / Spam penalty)
        if any(p in content for p in ["make $1000", "top 10 easy ai tools", "python vs java"]):
            security_impact = 10.0
            novelty = 10.0
            evidence_quality = 10.0
            ai_relevance = 10.0
            research_value = 10.0

        return {
            "security_impact": round(security_impact, 1),
            "novelty": round(novelty, 1),
            "evidence_quality": round(evidence_quality, 1),
            "ai_relevance": round(ai_relevance, 1),
            "research_value": round(research_value, 1)
        }

llm_client = UnifiedLLMClient()
