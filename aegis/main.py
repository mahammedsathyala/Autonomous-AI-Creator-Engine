import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from aegis.database import Base, engine, SessionLocal
from aegis.api.agent import router as agent_router
from aegis.api.feed import router as feed_router
from aegis.agent.scheduler import aegis_scheduler
from aegis.agent.lifecycle import create_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    Base.metadata.create_all(bind=engine)
    
    # Register default agent 'ada-sec-8f2a' if DB is fresh
    db = SessionLocal()
    try:
        if not aegis_scheduler.active_agents:
            aegis_scheduler.register_agent("ada-sec-8f2a", "Ada", "AI Security")
    finally:
        db.close()

    # Launch background scheduler task
    task = asyncio.create_task(aegis_scheduler.start_background_loop())
    yield
    aegis_scheduler.running = False
    task.cancel()

app = FastAPI(
    title="AEGIS Cyber Intelligence Autonomous Creator",
    description="Autonomous AI Cybersecurity persona engine featuring 5-dim deterministic scoring, belief engine, and live RSS ingestion.",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(feed_router)

@app.get("/health")
def health_check():
    return {"status": "ok", "app": "AEGIS Cyber Intelligence Platform"}

# Serve Dashboard static files
dashboard_dir = os.path.join(os.path.dirname(__file__), "dashboard")
if os.path.exists(dashboard_dir):
    app.mount("/static", StaticFiles(directory=dashboard_dir), name="static")

@app.get("/")
def serve_dashboard():
    index_path = os.path.join(dashboard_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"status": "running", "message": "AEGIS Cyber Intelligence Backend Active. Visit /docs for API schema."})
