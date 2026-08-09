import json
import re
import time
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from aegis.config import settings

class LLMProvider(ABC):
    """Abstract Base Class for LLM Providers."""
    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        pass

class DeterministicFallbackProvider(LLMProvider):
    """Deterministic Fallback Engine for offline execution, testing, and demo mode."""
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        content = prompt.lower()
        
        # Dimension Scoring logic for research items
        sec_terms = ["vulnerability", "cve", "zero-day", "exploit", "attack", "jailbreak", "injection", "breach", "threat", "patch"]
        sec_matches = [t for t in sec_terms if t in content]
        security_impact = min(100.0, 40.0 + (len(sec_matches) * 15.0))

        novelty = 70.0
        if any(w in content for w in ["arxiv", "2026", "new", "first", "zero-day", "breakthrough", "novel"]):
            novelty += 20.0

        evidence_quality = 65.0
        if any(w in content for w in ["cve", "nvd", "arxiv", "github", "advisory"]):
            evidence_quality += 25.0

        ai_terms = ["ai", "llm", "agent", "rag", "model", "prompt", "transformer", "vllm", "openai"]
        ai_matches = [t for t in ai_terms if t in content]
        ai_relevance = min(100.0, 35.0 + (len(ai_matches) * 18.0))

        research_value = 60.0
        if any(w in content for w in ["arxiv", "paper", "kernel", "benchmark"]):
            research_value += 30.0

        if any(p in content for p in ["make $1000", "top 10 easy ai tools", "python vs java"]):
            security_impact = novelty = evidence_quality = ai_relevance = research_value = 10.0

        return {
            "text": f"[AEGIS Deterministic Synthesis] Synthesized output for: {prompt[:80]}...",
            "security_impact": round(security_impact, 1),
            "novelty": round(novelty, 1),
            "evidence_quality": round(evidence_quality, 1),
            "ai_relevance": round(ai_relevance, 1),
            "research_value": round(research_value, 1),
            "tokens_used": 150,
            "cost_estimate": 0.0,
            "provider": "deterministic"
        }

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return DeterministicFallbackProvider().generate(prompt, system_prompt)
        try:
            import urllib.request
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are AEGIS AI System."},
                    {"role": "user", "content": prompt}
                ]
            }
            req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                result_text = data['choices'][0]['message']['content']
                usage = data.get('usage', {})
                tokens = usage.get('total_tokens', 200)
                return {"text": result_text, "tokens_used": tokens, "cost_estimate": round(tokens * 0.000002, 6), "provider": "openai"}
        except Exception as e:
            fallback = DeterministicFallbackProvider().generate(prompt, system_prompt)
            fallback["error"] = str(e)
            return fallback

class GroqProvider(LLMProvider):
    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        if not self.api_key:
            return DeterministicFallbackProvider().generate(prompt, system_prompt)
        try:
            import urllib.request
            headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}"}
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt or "You are AEGIS AI System."},
                    {"role": "user", "content": prompt}
                ]
            }
            req = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", data=json.dumps(payload).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                result_text = data['choices'][0]['message']['content']
                tokens = data.get('usage', {}).get('total_tokens', 180)
                return {"text": result_text, "tokens_used": tokens, "cost_estimate": 0.0, "provider": "groq"}
        except Exception as e:
            fallback = DeterministicFallbackProvider().generate(prompt, system_prompt)
            fallback["error"] = str(e)
            return fallback

class UnifiedLLMClient:
    """Provider-Agnostic LLM Interface with Fallback and Token Metrics."""
    def __init__(self):
        self.provider_type = settings.LLM_PROVIDER.lower()
        if self.provider_type == "openai" and settings.OPENAI_API_KEY:
            self.provider = OpenAIProvider(settings.OPENAI_API_KEY, settings.LLM_MODEL)
        elif self.provider_type == "groq" and settings.GROQ_API_KEY:
            self.provider = GroqProvider(settings.GROQ_API_KEY)
        else:
            self.provider = DeterministicFallbackProvider()

    def evaluate_topic_dimensions(self, title: str, summary: str, domain: str) -> Dict[str, Any]:
        prompt = f"Evaluate security topic for domain '{domain}': Title: {title}. Summary: {summary}"
        return self.provider.generate(prompt)

    def generate_completion(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        return self.provider.generate(prompt, system_prompt)

llm_client = UnifiedLLMClient()
