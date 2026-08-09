from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import json

from aegis.database import get_db
from aegis.schemas import FeedResponse, PostSchema
from aegis.models import PostModel, AgentModel
from aegis.agent.lifecycle import create_agent
from aegis.agent.scheduler import aegis_scheduler

router = APIRouter(tags=["feed"])

@router.get("/api/agent/feed", response_model=FeedResponse)
@router.get("/api/feed", response_model=FeedResponse)
def get_feed(agentId: str = Query(..., description="The agentId returned by init"), db: Session = Depends(get_db)):
    """
    GET /api/agent/feed?agentId=abc-123
    Returns published posts in reverse chronological order (newest first).
    """
    posts = db.query(PostModel).filter(PostModel.agent_id == agentId).order_by(PostModel.created_at.desc()).all()

    if not posts:
        # If agent is missing, auto-register and trigger cycle
        agent = db.query(AgentModel).filter(AgentModel.agent_id == agentId).first()
        if not agent:
            aegis_scheduler.register_agent(agent_id=agentId, name="Ada", domain="AI Security")
            posts = db.query(PostModel).filter(PostModel.agent_id == agentId).order_by(PostModel.created_at.desc()).all()

    formatted_posts = []
    for p in posts:
        try:
            sources_list = json.loads(p.sources)
        except Exception:
            sources_list = [p.sources] if p.sources else []

        formatted_posts.append(PostSchema(
            id=p.id,
            createdAt=p.created_at,
            text=p.text,
            rationale=p.rationale,
            sources=sources_list
        ))

    return FeedResponse(posts=formatted_posts)
