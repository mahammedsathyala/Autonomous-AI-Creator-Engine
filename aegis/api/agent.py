from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
import json

from aegis.database import get_db
from aegis.schemas import InitAgentRequest, InitAgentResponse
from aegis.agent.lifecycle import create_agent, get_agent
from aegis.agent.scheduler import aegis_scheduler
from aegis.agent.belief_engine import belief_engine
from aegis.models import PostModel, TopicEvaluationModel, MemoryItemModel, AgentModel

router = APIRouter(prefix="/api/agent", tags=["agent"])

@router.post("/init", response_model=InitAgentResponse)
def init_agent(req: Optional[InitAgentRequest] = None, db: Session = Depends(get_db)):
    """
    POST /api/agent/init
    Called exactly once before evaluation begins to initialize persona and agentId.
    """
    name = "Ada"
    domain = "AI Security"

    if req and req.persona:
        if req.persona.name:
            name = req.persona.name
        if req.persona.domain:
            domain = req.persona.domain

    agent = create_agent(db=db, name=name, domain=domain)
    aegis_scheduler.register_agent(agent_id=agent.agent_id, name=name, domain=domain)

    return {"agentId": agent.agent_id}

@router.get("/status")
def get_status(agentId: str = Query("ada-sec-8f2a"), db: Session = Depends(get_db)):
    agent = get_agent(db, agentId)
    if not agent:
        # Fallback query default or first agent
        agent = db.query(AgentModel).first()
        if not agent:
            agent = create_agent(db, "Ada", "AI Security")

    posts_count = db.query(PostModel).filter(PostModel.agent_id == agent.agent_id).count()
    evaluations = db.query(TopicEvaluationModel).filter(TopicEvaluationModel.agent_id == agent.agent_id).all()
    memories = db.query(MemoryItemModel).filter(MemoryItemModel.agent_id == agent.agent_id).all()
    beliefs = belief_engine.get_agent_beliefs(db, agent.agent_id)

    accepted_count = sum(1 for e in evaluations if e.status == "ACCEPTED")

    return {
        "agent": {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "domain": agent.domain,
            "editorial_voice": agent.editorial_voice,
            "rejection_standards": agent.rejection_standards
        },
        "metrics": {
            "totalPosts": posts_count,
            "totalEvaluations": len(evaluations),
            "acceptedTopics": accepted_count,
            "rejectedTopics": len(evaluations) - accepted_count,
            "acceptanceRate": round((accepted_count / len(evaluations) * 100), 1) if evaluations else 100.0,
            "memoryItemsCount": len(memories),
            "beliefsCount": len(beliefs)
        },
        "beliefs": [{"subject": b.subject, "statement": b.statement, "evidence_type": b.evidence_type, "confidence": b.confidence} for b in beliefs[:5]],
        "memories": [{"topic_key": m.topic_key, "summary": m.summary, "keywords": m.keywords.split(",")} for m in memories[:5]]
    }

@router.get("/rejections")
def get_rejections(agentId: str = Query("ada-sec-8f2a"), db: Session = Depends(get_db)):
    evaluations = db.query(TopicEvaluationModel).filter(TopicEvaluationModel.agent_id == agentId).order_by(TopicEvaluationModel.evaluated_at.desc()).limit(50).all()
    return {
        "evaluations": [
            {
                "id": e.id,
                "topic_title": e.topic_title,
                "source_url": e.source_url,
                "status": e.status,
                "score": e.score,
                "reason": e.reason,
                "evaluated_at": e.evaluated_at
            }
            for e in evaluations
        ]
    }

@router.post("/tick")
def manual_tick(agentId: str = Query("ada-sec-8f2a")):
    new_post = aegis_scheduler.trigger_tick(agentId)
    return {"status": "success", "published": True if new_post else False, "post": new_post}
