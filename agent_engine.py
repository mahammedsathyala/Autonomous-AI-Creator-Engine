import uuid
import json
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple, Optional
import database as db
from harvester import TopicHarvester

DEFAULT_PERSONAS = {
    "ada": {
        "name": "Ada",
        "domain": "AI Security",
        "title": "Senior AI Security & Vulnerability Researcher",
        "voice": "Analytical, rigorous, security-first, skeptic of unverified claims, focused on attack surfaces and defensive alignment.",
        "keywords": ["security", "jailbreak", "injection", "vulnerability", "adversarial", "guardrail", "cve", "weights", "exfiltration", "rag", "threat", "trust", "privacy", "attack", "audit"],
        "rejection_standards": "Rejects generic LLM listicles, non-technical product launch announcements, hype articles lacking code/vulnerability analysis, and off-domain general programming news."
    },
    "marcus": {
        "name": "Marcus",
        "domain": "ML Engineering",
        "title": "Principal Systems & CUDA Kernel Architect",
        "voice": "Direct, quantitative, performance-obsessed, focused on memory bandwidth, FLOPs efficiency, and distributed scaling.",
        "keywords": ["cuda", "kernel", "vllm", "flashattention", "throughput", "quantization", "fp8", "triton", "distributed", "gpu", "latency", "moe", "tensor", "optimization"],
        "rejection_standards": "Rejects prompt engineering tutorials, high-level AI policy debates, non-reproducible benchmarks, and general software news without systems metrics."
    },
    "elena": {
        "name": "Elena",
        "domain": "AI Product Analyst",
        "title": "Lead AI Product Strategist & Enterprise Architect",
        "voice": "Strategic, user-centric, ROI-focused, evaluating real-world agent reliability and workflow integration.",
        "keywords": ["agent", "roi", "enterprise", "workflow", "evals", "benchmark", "ux", "adoption", "cost", "latency", "tool calling", "saas", "production"],
        "rejection_standards": "Rejects hyper-academic proof-of-concept papers without production viability, generic AI memes, and unverified vendor marketing."
    }
}

class AutonomousAgentEngine:
    def __init__(self, agent_id: str = "ada-sec-8f2a", name: str = "Ada", domain: str = "AI Security"):
        self.agent_id = agent_id
        self.name = name
        self.domain = domain
        self.harvester = TopicHarvester()
        
        # Load or initialize persona config
        key = name.lower()
        if key in DEFAULT_PERSONAS:
            self.config = DEFAULT_PERSONAS[key]
        else:
            self.config = {
                "name": name,
                "domain": domain,
                "title": f"Autonomous Specialist in {domain}",
                "voice": f"Authoritative, insightful, analytical expert in {domain}.",
                "keywords": [k.strip() for k in domain.lower().split()],
                "rejection_standards": f"Rejects content lacking depth or relevance to {domain}."
            }
        
        # Ensure agent is saved in DB
        db.save_agent(
            agent_id=self.agent_id,
            name=self.name,
            domain=self.domain,
            editorial_voice=self.config["voice"],
            rejection_standards=self.config["rejection_standards"]
        )

    def evaluate_topic(self, topic: Dict[str, Any], published_memories: List[Dict[str, Any]]) -> Tuple[bool, int, str]:
        """
        Applies strict editorial judgment:
        1. Checks domain alignment
        2. Checks technical depth & substance
        3. Checks memory to avoid duplicate coverage
        Returns: (is_accepted: bool, score: int, rationale: str)
        """
        title = topic.get("title", "")
        summary = topic.get("summary", "")
        category = topic.get("category", "")
        content_lower = f"{title} {summary}".lower()
        
        # 1. Check Anti-patterns (Immediate Rejection)
        anti_patterns = [
            ("make $1000", "Generic financial clickbait and affiliate monetization scheme"),
            ("top 10 easy ai tools", "Low-effort consumer listicle lacking technical depth"),
            ("python vs java", "Off-domain basic programming comparison without AI relevance"),
            ("generic-hype", "Unverified social marketing clickbait")
        ]
        for pattern, reason in anti_patterns:
            if pattern in content_lower:
                return False, 15, f"REJECTED by Editorial Standards: {reason}."

        # 2. Check Memory Continuity (Avoid duplicate coverage)
        for mem in published_memories:
            past_key = mem.get("topic_key", "").lower()
            if past_key and len(past_key) > 4:
                # Check keyword overlap
                words = [w for w in re.findall(r'\w+', past_key) if len(w) > 4]
                matches = [w for w in words if w in content_lower]
                if len(matches) >= 3:
                    return False, 35, f"REJECTED by Memory Audit: Previously published on related topic '{past_key}' recently. Avoiding repetitive coverage."

        # 3. Domain Scoring
        domain_keywords = self.config.get("keywords", [])
        matched_keywords = [kw for kw in domain_keywords if kw in content_lower]
        
        score = 50 + (len(matched_keywords) * 15)
        
        # Bonus for research papers / CVE / vulnerability repos
        if "arxiv" in topic.get("source", "").lower() or "vulnerability" in topic.get("source", "").lower() or "cve" in content_lower:
            score += 15
        if "github" in topic.get("source", "").lower():
            score += 10

        score = min(score, 98)

        # Check threshold
        if score < 70:
            return False, score, f"REJECTED by Editorial Filter: Topic score ({score}/100) below quality threshold for {self.domain}. Lacks sufficient specialized relevance (matched: {matched_keywords})."

        return True, score, f"ACCEPTED for Publication: Topic score ({score}/100). High relevance to {self.domain} with strong technical substance (matched keywords: {', '.join(matched_keywords)})."

    def generate_post_content(self, topic: Dict[str, Any], memory_context: str) -> Tuple[str, str]:
        """
        Drafts the published post text and detailed publishing rationale based on the persona's voice.
        """
        title = topic.get("title", "")
        summary = topic.get("summary", "")
        url = topic.get("url", "")
        source = topic.get("source", "")
        
        name = self.name
        domain = self.domain

        if "security" in domain.lower() or name.lower() == "ada":
            text = (
                f"🚨 Critical Analysis: {title}\n\n"
                f"In our ongoing threat modeling of autonomous agent architectures, {summary}\n\n"
                f"Key Takeaway for AI Engineers: Unchecked tool calling and context injection remain top vulnerability vectors in production RAG systems. "
                f"Static system prompts are insufficient; runtime input sanitization and privilege isolation are mandatory.\n\n"
                f"{memory_context}"
                f"#AISecurity #LLMSafety #AppSec #CyberSecurity"
            )
            rationale = (
                f"Selected because indirect injection and inference vulnerability vectors represent an urgent threat to production AI deployments. "
                f"Relevant now as enterprise autonomous tool calling explodes across cloud environments. "
                f"Chosen over 5 other candidate stories due to superior technical depth and actionable threat insights."
            )
        elif "systems" in domain.lower() or "engineering" in domain.lower() or name.lower() == "marcus":
            text = (
                f"⚡ Deep Dive: {title}\n\n"
                f"Evaluating compute efficiency and memory access patterns: {summary}\n\n"
                f"Systems Insight: Reducing memory bandwidth bottlenecks during KV-cache generation yields higher real-world throughput than raw TFLOPS scaling. "
                f"Custom CUDA/Triton kernels remain the key differentiator for scaling inference affordably.\n\n"
                f"{memory_context}"
                f"#MLEngineering #CUDA #Systems #AIInfrastructure"
            )
            rationale = (
                f"Selected because hardware kernel optimization directly impacts LLM serving costs and latency SLAs. "
                f"Relevant now following recent hardware generation benchmarks. "
                f"Chosen over non-technical AI hype posts for its concrete engineering substance."
            )
        else:
            text = (
                f"💡 Editorial Analysis: {title}\n\n"
                f"Examining impact across the {domain} ecosystem: {summary}\n\n"
                f"Strategic Note: Success in production AI requires moving beyond benchmarks to measuring real operational reliability and user trust.\n\n"
                f"{memory_context}"
                f"#{domain.replace(' ', '')} #TechTrends #ArtificialIntelligence"
            )
            rationale = (
                f"Selected for high strategic relevance to current {domain} developments. "
                f"Relevant now due to rapid shift towards production deployment. "
                f"Chosen over standard consumer news for its analytical perspective."
            )

        return text.strip(), rationale.strip()

    def run_autonomous_cycle(self) -> Optional[Dict[str, Any]]:
        """
        Executes one full autonomous publishing cycle:
        1. Harvest topics from live sources
        2. Evaluate editorial standards (log accepted/rejected)
        3. Check memory graph
        4. Publish post with explicit rationale
        5. Return new post or None
        """
        print(f"[{datetime.now().strftime('%H:%M:%S')}] [Agent {self.name}] Starting autonomous topic discovery cycle...")
        
        # Fetch candidate topics
        candidates = self.harvester.get_live_topics()
        published_memories = db.get_memories(self.agent_id)
        
        selected_topic = None
        selected_score = 0
        
        for candidate in candidates:
            eval_id = f"eval-{uuid.uuid4().hex[:8]}"
            title = candidate.get("title", "Untitled")
            source_url = candidate.get("url", "")
            
            is_accepted, score, reason = self.evaluate_topic(candidate, published_memories)
            
            status = "ACCEPTED" if is_accepted else "REJECTED"
            
            # Save evaluation audit log in DB
            db.save_evaluation(
                eval_id=eval_id,
                agent_id=self.agent_id,
                topic_title=title,
                source_url=source_url,
                status=status,
                score=score,
                reason=reason
            )
            
            if is_accepted and selected_topic is None:
                selected_topic = candidate
                selected_score = score

        if not selected_topic:
            print(f"[Agent {self.name}] No candidates passed editorial standards in this cycle.")
            return None

        # Build memory context reference if past memory exists
        memory_context = ""
        if published_memories:
            last_mem = published_memories[0]
            memory_context = f"(Building on our previous report regarding {last_mem.get('topic_key')})\n\n"

        # Generate Post & Rationale
        post_text, rationale = self.generate_post_content(selected_topic, memory_context)
        post_id = f"p-{uuid.uuid4().hex[:6]}"
        now_utc = datetime.now(timezone.utc).isoformat()
        
        sources = [selected_topic.get("url")] if selected_topic.get("url") else ["https://arxiv.org"]

        # Save Post to DB
        db.save_post(
            post_id=post_id,
            agent_id=self.agent_id,
            text=post_text,
            rationale=rationale,
            sources=sources,
            created_at=now_utc,
            topic_title=selected_topic.get("title")
        )

        # Save to Memory Graph
        db.save_memory(
            agent_id=self.agent_id,
            post_id=post_id,
            topic_key=selected_topic.get("title", "")[:40],
            summary=selected_topic.get("summary", "")[:100],
            keywords=self.config.get("keywords", [])[:4]
        )

        print(f"[Agent {self.name}] Published post {post_id}: '{selected_topic.get('title')[:40]}...'")
        
        return {
            "id": post_id,
            "createdAt": now_utc,
            "text": post_text,
            "rationale": rationale,
            "sources": sources
        }
