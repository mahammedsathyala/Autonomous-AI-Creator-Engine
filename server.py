import asyncio
import os
import uuid
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field

import database as db
from scheduler import global_scheduler

app = FastAPI(
    title="Autonomous AI Creator API",
    description="Autonomous AI Agent system that discovers topics, exercises editorial judgment, remembers past posts, and continuously publishes over time.",
    version="1.0.0"
)

# Enable CORS for cross-origin evaluation
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Schemas for validation
class PersonaModel(BaseModel):
    name: str = Field(default="Ada", description="Name of persona")
    domain: str = Field(default="AI Security", description="Domain of expertise")

class InitAgentRequest(BaseModel):
    persona: Optional[PersonaModel] = Field(default_factory=PersonaModel)

class InitAgentResponse(BaseModel):
    agentId: str

@app.on_event("startup")
async def startup_event():
    """Starts the background loop on server startup and initializes default Ada agent asynchronously."""
    db.init_db()
    # Register default agent asynchronously
    asyncio.create_task(async_register_default())
    # Launch continuous background loop
    asyncio.create_task(global_scheduler.start_background_loop())

async def async_register_default():
    await asyncio.sleep(0.1)
    global_scheduler.register_agent(
        agent_id="ada-sec-8f2a",
        name="Ada",
        domain="AI Security"
    )

# Endpoint 1: Initialize Agent (POST /api/agent/init)
@app.post("/api/agent/init", response_model=InitAgentResponse)
async def init_agent(req: Optional[InitAgentRequest] = None):
    """
    Called exactly once before evaluation begins.
    Initializes agent with target persona and triggers immediate first cycle.
    """
    name = "Ada"
    domain = "AI Security"
    
    if req and req.persona:
        if req.persona.name:
            name = req.persona.name
        if req.persona.domain:
            domain = req.persona.domain

    # Generate a reproducible / clean agentId based on persona or uuid
    clean_name = name.lower().replace(" ", "")
    clean_domain = domain.lower().replace(" ", "")[:4]
    agent_id = f"{clean_name}-{clean_domain}-{uuid.uuid4().hex[:4]}"

    # Register agent with scheduler and trigger initial autonomous cycle
    global_scheduler.register_agent(
        agent_id=agent_id,
        name=name,
        domain=domain
    )

    return {"agentId": agent_id}

# Endpoint 2: Retrieve Feed (GET /api/agent/feed?agentId=abc-123)
@app.get("/api/agent/feed")
async def get_feed(agentId: str = Query(..., description="The agentId returned by init")):
    """
    Evaluator queries this endpoint to retrieve published posts in reverse chronological order.
    """
    # If agentId wasn't registered in current memory session, check DB
    agent_info = db.get_agent(agentId)
    if not agent_info:
        # Auto-register default fallback for safety if an unregistered ID is requested
        global_scheduler.register_agent(agent_id=agentId, name="Ada", domain="AI Security")

    posts = db.get_posts(agentId)
    
    # Format according to API requirement
    formatted_posts = []
    for p in posts:
        formatted_posts.append({
            "id": p["id"],
            "createdAt": p["createdAt"],
            "text": p["text"],
            "rationale": p["rationale"],
            "sources": p["sources"]
        })

    return {"posts": formatted_posts}

# Supplementary Endpoints for Visual UI & Analytics
@app.get("/api/agent/status")
async def get_status(agentId: str = Query("ada-sec-8f2a")):
    agent_info = db.get_agent(agentId) or {
        "agent_id": agentId,
        "name": "Ada",
        "domain": "AI Security",
        "editorial_voice": "Analytical, security-first",
        "rejection_standards": "Rejects clickbait and non-technical hype"
    }
    posts = db.get_posts(agentId)
    evaluations = db.get_evaluations(agentId, limit=100)
    memories = db.get_memories(agentId)

    accepted_count = sum(1 for e in evaluations if e["status"] == "ACCEPTED")
    rejected_count = sum(1 for e in evaluations if e["status"] == "REJECTED")

    return {
        "agent": agent_info,
        "metrics": {
            "totalPosts": len(posts),
            "totalEvaluations": len(evaluations),
            "acceptedTopics": accepted_count,
            "rejectedTopics": rejected_count,
            "acceptanceRate": round((accepted_count / len(evaluations) * 100), 1) if evaluations else 100.0,
            "memoryItemsCount": len(memories),
            "isBackgroundLoopActive": global_scheduler.running,
            "intervalSeconds": global_scheduler.interval_seconds
        },
        "memories": memories[:10]
    }

@app.get("/api/agent/rejections")
async def get_rejections(agentId: str = Query("ada-sec-8f2a")):
    evaluations = db.get_evaluations(agentId, limit=50)
    return {"evaluations": evaluations}

@app.post("/api/agent/tick")
async def manual_tick(agentId: str = Query("ada-sec-8f2a")):
    """Forces an immediate discovery and publishing cycle (useful for live demo testing)."""
    new_post = global_scheduler.trigger_tick(agentId)
    return {
        "status": "success",
        "published": True if new_post else False,
        "post": new_post
    }

# Serve Frontend static assets
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def serve_index():
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return JSONResponse({"message": "Autonomous AI Creator API Running. Visit /docs for OpenAPI documentation."})
