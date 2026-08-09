from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Boolean
from datetime import datetime, timezone
from aegis.database import Base

def now_utc():
    return datetime.now(timezone.utc).isoformat()

# --- 1. PRESERVED RESEARCH MODE MODELS ---

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
    sources = Column(Text, nullable=False)
    topic_title = Column(String, nullable=True)
    score = Column(Float, default=0.0)

class TopicEvaluationModel(Base):
    __tablename__ = "topic_evaluations"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    topic_title = Column(String, nullable=False)
    source_url = Column(String, nullable=True)
    status = Column(String, nullable=False)
    score = Column(Float, nullable=False)
    score_breakdown = Column(Text, nullable=True)
    reason = Column(Text, nullable=False)
    evaluated_at = Column(String, default=now_utc)

class BeliefModel(Base):
    __tablename__ = "beliefs"

    id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, nullable=False, index=True)
    subject = Column(String, nullable=False)
    statement = Column(Text, nullable=False)
    evidence_type = Column(String, nullable=False)
    confidence = Column(Float, default=0.8)
    status = Column(String, default="ACTIVE")
    source_references = Column(Text, default="[]")
    supporting_events = Column(Text, default="[]")
    contradicting_events = Column(Text, default="[]")
    created_at = Column(String, default=now_utc)
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


# --- 2. CREATOR MODE AUTONOMOUS SOFTWARE ENGINEERING MODELS (18 TABLES) ---

class UserModel(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    role = Column(String, default="ADMIN")
    created_at = Column(String, default=now_utc)

class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="CREATED", index=True)
    current_state = Column(String, default="CREATED")
    quality_gate_passed = Column(Boolean, default=False)
    created_at = Column(String, default=now_utc)
    updated_at = Column(String, default=now_utc)
    config_json = Column(Text, default="{}")

class ProjectVersionModel(Base):
    __tablename__ = "project_versions"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    version_number = Column(String, nullable=False)
    commit_sha = Column(String, nullable=True)
    changelog = Column(Text, nullable=True)
    created_at = Column(String, default=now_utc)

class TaskModel(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    task_code = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    parent_task = Column(String, nullable=True)
    dependencies = Column(Text, default="[]") # JSON list of task_codes
    status = Column(String, default="PENDING")
    priority = Column(Integer, default=1)
    assigned_agent = Column(String, default="Coder")
    input_json = Column(Text, default="{}")
    output_json = Column(Text, default="{}")
    retry_count = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
    created_at = Column(String, default=now_utc)
    started_at = Column(String, nullable=True)
    completed_at = Column(String, nullable=True)

class AgentRunModel(Base):
    __tablename__ = "agent_runs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    task_id = Column(String, nullable=True)
    agent_name = Column(String, nullable=False)
    state = Column(String, nullable=False)
    input_data = Column(Text, default="{}")
    output_data = Column(Text, default="{}")
    duration_ms = Column(Integer, default=0)
    status = Column(String, default="SUCCESS")
    error_msg = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_estimate = Column(Float, default=0.0)
    created_at = Column(String, default=now_utc)

class ExecutionModel(Base):
    __tablename__ = "executions"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    command = Column(Text, nullable=False)
    exit_code = Column(Integer, default=0)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0)
    executed_at = Column(String, default=now_utc)

class StateTransitionModel(Base):
    __tablename__ = "state_transitions"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    from_state = Column(String, nullable=False)
    to_state = Column(String, nullable=False)
    triggered_by = Column(String, nullable=False)
    timestamp = Column(String, default=now_utc)
    details_json = Column(Text, default="{}")

class MemoryEpisodicModel(Base):
    __tablename__ = "memory_episodic"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=False, index=True)
    task_code = Column(String, nullable=True)
    action = Column(String, nullable=False)
    result = Column(Text, nullable=False)
    status = Column(String, default="SUCCESS")
    timestamp = Column(String, default=now_utc)

class MemorySemanticModel(Base):
    __tablename__ = "memory_semantic"

    id = Column(String, primary_key=True, index=True)
    concept = Column(String, nullable=False, index=True)
    definition = Column(Text, nullable=False)
    tags = Column(String, default="")
    created_at = Column(String, default=now_utc)

class MemoryProjectModel(Base):
    __tablename__ = "memory_project"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    key = Column(String, nullable=False)
    value_json = Column(Text, nullable=False)
    updated_at = Column(String, default=now_utc)

class MemoryFailureModel(Base):
    __tablename__ = "memory_failure"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=True, index=True)
    error_signature = Column(String, nullable=False, index=True)
    error_context = Column(Text, nullable=False)
    solution = Column(Text, nullable=False)
    success_count = Column(Integer, default=1)
    created_at = Column(String, default=now_utc)

class ToolCallModel(Base):
    __tablename__ = "tool_calls"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    agent_name = Column(String, nullable=False)
    tool_name = Column(String, nullable=False)
    target = Column(String, nullable=True)
    status = Column(String, default="SUCCESS")
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    duration_ms = Column(Integer, default=0)
    timestamp = Column(String, default=now_utc)

class ArtifactModel(Base):
    __tablename__ = "artifacts"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    name = Column(String, nullable=False)
    artifact_type = Column(String, nullable=False) # CODE, DOC, SPEC, BINARY
    file_path = Column(String, nullable=False)
    size_bytes = Column(Integer, default=0)
    created_at = Column(String, default=now_utc)

class TestRunModel(Base):
    __tablename__ = "test_runs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    total_tests = Column(Integer, default=0)
    passed_tests = Column(Integer, default=0)
    failed_tests = Column(Integer, default=0)
    coverage_pct = Column(Float, default=100.0)
    stdout = Column(Text, nullable=True)
    stderr = Column(Text, nullable=True)
    run_at = Column(String, default=now_utc)

class ReviewModel(Base):
    __tablename__ = "reviews"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    agent_name = Column(String, default="ReviewerAgent")
    score = Column(Float, default=100.0)
    findings_json = Column(Text, default="[]")
    approved = Column(Boolean, default=True)
    created_at = Column(String, default=now_utc)

class SecurityFindingModel(Base):
    __tablename__ = "security_findings"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    severity = Column(String, nullable=False) # LOW, MEDIUM, HIGH, CRITICAL
    category = Column(String, nullable=False) # SECRETS, INJECTION, TRAVERSAL, SUBPROCESS
    description = Column(Text, nullable=False)
    resolved = Column(Boolean, default=True)
    created_at = Column(String, default=now_utc)

class GitCommitModel(Base):
    __tablename__ = "git_commits"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    commit_sha = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    branch = Column(String, default="main")
    committed_at = Column(String, default=now_utc)

class ApprovalGateModel(Base):
    __tablename__ = "approval_gates"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    action_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    command = Column(Text, nullable=True)
    status = Column(String, default="PENDING")
    requested_at = Column(String, default=now_utc)
    decided_at = Column(String, nullable=True)

class DeploymentModel(Base):
    __tablename__ = "deployments"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, index=True)
    environment = Column(String, default="LOCAL_SANDBOX")
    endpoint_url = Column(String, nullable=True)
    status = Column(String, default="SUCCESS")
    deployed_at = Column(String, default=now_utc)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, nullable=True, index=True)
    actor = Column(String, nullable=False)
    event_type = Column(String, nullable=False)
    payload_json = Column(Text, default="{}")
    timestamp = Column(String, default=now_utc)

class MetricsSummaryModel(Base):
    __tablename__ = "metrics_summary"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False, unique=True)
    total_tasks = Column(Integer, default=0)
    successful_tasks = Column(Integer, default=0)
    repair_success_rate = Column(Float, default=0.0)
    test_pass_rate = Column(Float, default=0.0)
    security_pass_rate = Column(Float, default=100.0)
    llm_calls = Column(Integer, default=0)
    tokens_used = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    avg_duration_sec = Column(Float, default=0.0)
    updated_at = Column(String, default=now_utc)
