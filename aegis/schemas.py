from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

# --- PRESERVED RESEARCH SCHEMAS ---

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
    status: Optional[str] = "ACTIVE"
    source_references: Optional[List[str]] = []
    created_at: Optional[str] = None
    updated_at: str


# --- CREATOR MODE AUTONOMOUS SOFTWARE ENGINEERING SCHEMAS ---

class CreateProjectRequest(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Natural language software idea / requirements")
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    current_state: str
    quality_gate_passed: bool = False
    created_at: str
    updated_at: str
    config_json: Optional[str] = "{}"

class TaskSchema(BaseModel):
    id: str
    project_id: str
    task_code: str
    title: str
    description: str
    dependencies: List[str] = []
    status: str
    assigned_agent: str
    created_at: str
    completed_at: Optional[str] = None

class StateTransitionSchema(BaseModel):
    id: str
    project_id: str
    from_state: str
    to_state: str
    triggered_by: str
    timestamp: str

class ApprovalGateSchema(BaseModel):
    id: str
    project_id: str
    action_type: str
    description: str
    command: Optional[str] = None
    status: str
    requested_at: str
    decided_at: Optional[str] = None

class SecurityFindingSchema(BaseModel):
    id: str
    project_id: str
    severity: str
    category: str
    description: str
    resolved: bool
    created_at: str

class ReviewSchema(BaseModel):
    id: str
    project_id: str
    agent_name: str
    score: float
    approved: bool
    created_at: str

class MetricsSummarySchema(BaseModel):
    total_projects: int = 0
    completed_projects: int = 0
    success_rate: float = 0.0
    total_tasks: int = 0
    successful_tasks: int = 0
    task_completion_rate: float = 0.0
    repair_success_rate: float = 0.0
    security_pass_rate: float = 100.0
    llm_calls: int = 0
    tokens_used: int = 0
    cost_usd: float = 0.0
