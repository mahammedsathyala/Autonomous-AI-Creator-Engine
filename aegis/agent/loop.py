import uuid
import json
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from aegis.models import MemoryItemModel, TopicEvaluationModel, now_utc
from aegis.agent.discoverer import discoverer
from aegis.agent.embeddings import similarity_engine
from aegis.agent.scorer import topic_scorer
from aegis.agent.writer import research_writer

def run_research_cycle(db: Session, agent_id: str, persona_name: str = "Ada", persona_domain: str = "AI Security") -> Optional[Dict[str, Any]]:
    """
    Executes one complete research cycle:
    RSS Ingestion -> Deduplication -> 5-Dim Scorer -> Decision Engine -> Writer -> Belief Update
    """
    candidates = discoverer.get_live_topics()
    
    # Load past memories for deduplication
    memories = db.query(MemoryItemModel).filter(MemoryItemModel.agent_id == agent_id).all()
    past_mem_dicts = [{"topic_key": m.topic_key, "source_url": ""} for m in memories]

    selected_topic = None
    selected_score = 0.0

    for candidate in candidates:
        title = candidate.get("title", "Untitled")
        url = candidate.get("url", "")
        summary = candidate.get("summary", "")

        # 1. Deduplication Check
        is_dup, dup_reason = similarity_engine.is_duplicate(title, url, past_mem_dicts)
        if is_dup:
            eval_id = f"eval-{uuid.uuid4().hex[:8]}"
            eval_record = TopicEvaluationModel(
                id=eval_id,
                agent_id=agent_id,
                topic_title=title,
                source_url=url,
                status="REJECTED",
                score=35.0,
                score_breakdown=json.dumps({"dup_penalty": 35.0}),
                reason=f"REJECTED by Deduplication Engine: {dup_reason}",
                evaluated_at=now_utc()
            )
            db.add(eval_record)
            db.commit()
            continue

        # 2. 5-Dimensional Deterministic Scoring
        status, score, dims, reason = topic_scorer.score_topic(title, summary, persona_domain)

        eval_id = f"eval-{uuid.uuid4().hex[:8]}"
        eval_record = TopicEvaluationModel(
            id=eval_id,
            agent_id=agent_id,
            topic_title=title,
            source_url=url,
            status=status,
            score=score,
            score_breakdown=json.dumps(dims),
            reason=reason,
            evaluated_at=now_utc()
        )
        db.add(eval_record)
        db.commit()

        if status == "ACCEPTED" and selected_topic is None:
            selected_topic = candidate
            selected_score = score

    if not selected_topic:
        return None

    # 3. Publish Post
    post_data = research_writer.draft_and_publish(
        db=db,
        agent_id=agent_id,
        topic=selected_topic,
        score=selected_score,
        persona_name=persona_name,
        persona_domain=persona_domain
    )

    return post_data
