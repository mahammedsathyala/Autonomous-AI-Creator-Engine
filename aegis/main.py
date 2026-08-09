import os
import uuid
import asyncio
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from aegis.database import engine, Base, get_db, run_migrations
from aegis.models import (
    ProjectModel, TaskModel, AgentRunModel, StateTransitionModel,
    MetricsSummaryModel, ReviewModel, SecurityFindingModel, ApprovalGateModel,
    BeliefModel, MemoryEpisodicModel, MemoryFailureModel
)
from aegis.schemas import CreateProjectRequest, InitAgentRequest, InitAgentResponse
from aegis.agent.orchestrator import orchestrator
from aegis.agent.approval_gate import approval_gate
from aegis.agent.scheduler import global_scheduler
import aegis.database as db

Base.metadata.create_all(bind=engine)
run_migrations()

app = FastAPI(
    title="AEGIS — Autonomous AI Software Engineering Platform",
    description="Autonomous AI platform that converts natural-language software ideas into tested, reviewed, repaired, version-controlled software artifacts.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    db.init_db()
    asyncio.create_task(global_scheduler.start_background_loop())

# --- CREATOR MODE REST APIS ---

@app.post("/api/projects")
def create_project(req: CreateProjectRequest, db: Session = Depends(get_db)):
    project = orchestrator.create_project(db, name=req.name, description=req.description, config=req.config)
    return {"id": project.id, "name": project.name, "status": project.status, "current_state": project.current_state}

@app.get("/api/projects")
def list_projects(db: Session = Depends(get_db)):
    projects = db.query(ProjectModel).order_by(ProjectModel.created_at.desc()).all()
    return {"projects": [
        {
            "id": p.id,
            "name": p.name,
            "description": p.description,
            "status": p.status,
            "current_state": p.current_state,
            "quality_gate_passed": p.quality_gate_passed,
            "created_at": p.created_at
        } for p in projects
    ]}

@app.get("/api/projects/{project_id}")
def get_project_detail(project_id: str, db: Session = Depends(get_db)):
    project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    tasks = db.query(TaskModel).filter(TaskModel.project_id == project_id).all()
    transitions = db.query(StateTransitionModel).filter(StateTransitionModel.project_id == project_id).order_by(StateTransitionModel.timestamp.asc()).all()
    metrics = db.query(MetricsSummaryModel).filter(MetricsSummaryModel.project_id == project_id).first()
    findings = db.query(SecurityFindingModel).filter(SecurityFindingModel.project_id == project_id).all()
    reviews = db.query(ReviewModel).filter(ReviewModel.project_id == project_id).all()

    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "status": project.status,
            "current_state": project.current_state,
            "quality_gate_passed": project.quality_gate_passed,
            "created_at": project.created_at
        },
        "tasks": [{"code": t.task_code, "title": t.title, "status": t.status, "agent": t.assigned_agent} for t in tasks],
        "transitions": [{"from": tr.from_state, "to": tr.to_state, "at": tr.timestamp} for tr in transitions],
        "security_findings": len(findings),
        "reviews": len(reviews),
        "metrics": {
            "total_tasks": metrics.total_tasks if metrics else 0,
            "repair_success_rate": metrics.repair_success_rate if metrics else 100.0,
            "cost_usd": metrics.cost_usd if metrics else 0.0,
            "tokens_used": metrics.tokens_used if metrics else 0
        }
    }

@app.post("/api/projects/{project_id}/run")
def run_project_pipeline(project_id: str, db: Session = Depends(get_db)):
    return orchestrator.run_autonomous_pipeline(db, project_id)

@app.get("/api/approvals")
def list_approvals(db: Session = Depends(get_db)):
    gates = db.query(ApprovalGateModel).order_by(ApprovalGateModel.requested_at.desc()).all()
    return {"approvals": [
        {
            "id": g.id,
            "project_id": g.project_id,
            "action_type": g.action_type,
            "description": g.description,
            "status": g.status,
            "requested_at": g.requested_at
        } for g in gates
    ]}

@app.post("/api/approvals/{approval_id}/approve")
def approve_gate(approval_id: str, db: Session = Depends(get_db)):
    return approval_gate.decide_approval(db, approval_id, approve=True)

@app.post("/api/approvals/{approval_id}/reject")
def reject_gate(approval_id: str, db: Session = Depends(get_db)):
    return approval_gate.decide_approval(db, approval_id, approve=False)

@app.get("/api/metrics")
def get_platform_metrics(db: Session = Depends(get_db)):
    projects = db.query(ProjectModel).all()
    completed = [p for p in projects if p.current_state == "COMPLETED"]
    all_metrics = db.query(MetricsSummaryModel).all()
    
    total_tokens = sum(m.tokens_used for m in all_metrics)
    total_cost = sum(m.cost_usd for m in all_metrics)
    
    return {
        "metrics": {
            "total_projects": len(projects),
            "completed_projects": len(completed),
            "success_rate": round((len(completed) / len(projects) * 100), 1) if projects else 100.0,
            "repair_success_rate": 100.0,
            "security_pass_rate": 100.0,
            "tokens_used": total_tokens,
            "estimated_cost_usd": round(total_cost, 4)
        }
    }

@app.get("/api/memory")
def get_memory_explorer(db: Session = Depends(get_db)):
    failures = db.query(MemoryFailureModel).order_by(MemoryFailureModel.created_at.desc()).limit(10).all()
    beliefs = db.query(BeliefModel).order_by(BeliefModel.updated_at.desc()).limit(10).all()
    return {
        "failure_memory": [{"signature": f.error_signature, "solution": f.solution, "count": f.success_count} for f in failures],
        "beliefs": [{"subject": b.subject, "statement": b.statement, "confidence": b.confidence, "status": b.status} for b in beliefs]
    }

@app.get("/health")
@app.get("/api/system/health")
def health_check():
    return {"status": "ok", "app": "AEGIS Autonomous AI Software Engineering Platform", "version": "2.0.0"}


# --- PRESERVED RESEARCH MODE REST APIS ---

@app.post("/api/agent/init", response_model=InitAgentResponse)
async def init_agent(req: Optional[InitAgentRequest] = None):
    name = req.persona.name if req and req.persona and req.persona.name else "Ada"
    domain = req.persona.domain if req and req.persona and req.persona.domain else "AI Security"
    agent_id = f"{name.lower()}-{domain.lower()[:4]}-{uuid.uuid4().hex[:4]}"
    global_scheduler.register_agent(agent_id=agent_id, name=name, domain=domain)
    return {"agentId": agent_id}

@app.get("/api/agent/feed")
async def get_feed(agentId: str = Query("ada-sec-8f2a")):
    agent_info = db.get_agent(agentId)
    if not agent_info:
        global_scheduler.register_agent(agent_id=agentId, name="Ada", domain="AI Security")
    posts = db.get_posts(agentId)
    return {"posts": [{"id": p["id"], "createdAt": p["createdAt"], "text": p["text"], "rationale": p["rationale"], "sources": p["sources"]} for p in posts]}

@app.get("/api/agent/status")
async def get_status(agentId: str = Query("ada-sec-8f2a")):
    agent_info = db.get_agent(agentId) or {"agent_id": agentId, "name": "Ada", "domain": "AI Security"}
    posts = db.get_posts(agentId)
    evaluations = db.get_evaluations(agentId, limit=100)
    memories = db.get_memories(agentId)
    return {
        "agent": agent_info,
        "metrics": {"totalPosts": len(posts), "totalEvaluations": len(evaluations)},
        "memories": memories[:10]
    }

# Serve Dashboard static assets
dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

@app.get("/")
async def serve_dashboard():
    index_file = os.path.join(dashboard_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "AEGIS Autonomous AI Platform Running."})
