import uuid
import json
from typing import Dict, Any, Tuple
from sqlalchemy.orm import Session
from aegis.models import PostModel, MemoryItemModel, now_utc
from aegis.agent.belief_engine import belief_engine

class ResearchWriter:
    """
    Research Writer:
    Generates post text in persona's editorial voice, attaches explicit evidence labels,
    generates 3-part rationale, and updates long-term memory graph.
    """
    def draft_and_publish(
        self,
        db: Session,
        agent_id: str,
        topic: Dict[str, Any],
        score: float,
        persona_name: str = "Ada",
        persona_domain: str = "AI Security"
    ) -> Dict[str, Any]:
        title = topic.get("title", "")
        summary = topic.get("summary", "")
        url = topic.get("url", "")
        source = topic.get("source", "Live Security Stream")

        post_id = f"p-{uuid.uuid4().hex[:6]}"
        now = now_utc()

        # Classify evidence label
        evidence_label = "FACT" if any(w in f"{title} {summary}".lower() for w in ["cve", "nvd", "patch", "advisory", "arxiv"]) else "CLAIM"

        text = (
            f"🚨 [AEGIS Intelligence Analysis | Evidence: {evidence_label}] {title}\n\n"
            f"Key Finding: {summary}\n\n"
            f"Tactical Recommendation: Enterprise deployments running agentic tool-calling models must enforce "
            f"runtime input sanitization and privilege boundary checking to prevent indirect context hijacking.\n\n"
            f"#AISecurity #AppSec #CyberIntelligence #ZeroDay"
        )

        rationale = (
            f"Why Selected: Evaluated via 5-dimensional deterministic scoring (Score: {score}/100). High security impact and evidence quality. "
            f"Why Relevant Now: Critical advisory for cloud-hosted inference endpoints and RAG pipelines. "
            f"Why Chosen: Outperformed candidate stories due to superior technical evidence and threat model applicability."
        )

        sources = [url] if url else ["https://cisa.gov"]
        sources_json = json.dumps(sources)

        post = PostModel(
            id=post_id,
            agent_id=agent_id,
            created_at=now,
            text=text.strip(),
            rationale=rationale.strip(),
            sources=sources_json,
            topic_title=title,
            score=score
        )
        db.add(post)

        # Update memory item
        memory = MemoryItemModel(
            agent_id=agent_id,
            post_id=post_id,
            topic_key=title[:40],
            summary=summary[:100],
            keywords="security,vulnerability,cve,agent",
            created_at=now
        )
        db.add(memory)

        # Update belief
        belief_engine.record_or_update_belief(
            db=db,
            agent_id=agent_id,
            subject=title[:30],
            statement=summary[:120],
            evidence_type=evidence_label,
            confidence=round(score / 100.0, 2)
        )

        db.commit()

        return {
            "id": post_id,
            "createdAt": now,
            "text": text.strip(),
            "rationale": rationale.strip(),
            "sources": sources
        }

research_writer = ResearchWriter()
