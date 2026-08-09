from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class PersonaSchema(BaseModel):
    name: str = Field(default="Ada", description="Name of persona")
    domain: str = Field(default="AI Security", description="Domain of expertise")

class InitAgentRequest(BaseModel):
    persona: Optional[PersonaSchema] = Field(default_factory=PersonaSchema)

class InitAgentResponse(BaseModel):
    agentId: str

class PostSchema(BaseModel):
    id: str
    createdAt: str
    text: str
    rationale: str
    sources: List[str]

class FeedResponse(BaseModel):
    posts: List[PostSchema]

class EvaluationSchema(BaseModel):
    id: str
    topic_title: str
    source_url: Optional[str]
    status: str
    score: float
    score_breakdown: Optional[Dict[str, float]]
    reason: str
    evaluated_at: str

class BeliefSchema(BaseModel):
    id: str
    subject: str
    statement: str
    evidence_type: str
    confidence: float
    updated_at: str
