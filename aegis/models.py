from sqlalchemy import Column, String, Integer, Float, Text, DateTime
from datetime import datetime, timezone
from aegis.database import Base

def now_utc():
    return datetime.now(timezone.utc).isoformat()

class AgentModel(Base):
    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    editorial_voice = Column(Text, nullable=True)
    rejection_standards = Column(Text, nullable=True)
    created_at = Column(String, default=now_utc)

class PostModel(Base):
    __tablename__ = "posts"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    created_at = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    rationale = Column(Text, nullable=False)
    sources = Column(Text, nullable=False) # JSON array string
    topic_title = Column(String, nullable=True)
    score = Column(Float, default=0.0)

class TopicEvaluationModel(Base):
    __tablename__ = "topic_evaluations"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    topic_title = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    status = Column(String, nullable=False) # 'ACCEPTED', 'HOLD', 'REJECTED'
    score = Column(Float, nullable=False)
    score_breakdown = Column(Text, nullable=True) # JSON string of 5 dimensions
    reason = Column(Text, nullable=False)
    evaluated_at = Column(String, default=now_utc)

class BeliefModel(Base):
    __tablename__ = "beliefs"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    statement = Column(Text, nullable=False)
    evidence_type = Column(String, nullable=False) # FACT, CLAIM, INFERENCE, UNCERTAINTY
    confidence = Column(Float, default=0.8) # 0.0 to 1.0
    updated_at = Column(String, default=now_utc)

class MemoryItemModel(Base):
    __tablename__ = "memory_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(String, nullable=False, index=True)
    post_id = Column(String, nullable=False)
    topic_key = Column(String, nullable=False)
    summary = Column(Text, nullable=False)
    keywords = Column(String, nullable=False)
    created_at = Column(String, default=now_utc)
