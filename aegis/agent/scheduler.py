import asyncio
from typing import Dict, Any
from aegis.config import settings
from aegis.database import SessionLocal
from aegis.agent.lifecycle import restore_agents
from aegis.agent.loop import run_research_cycle

class AegisScheduler:
    """
    Scheduler wrapper running periodic background research cycles across active agents.
    Respects FIRST_CYCLE_DELAY_SECONDS and CYCLE_INTERVAL_SECONDS.
    """
    def __init__(self):
        self.active_agents: Dict[str, Dict[str, Any]] = {}
        self.running = False

    def register_agent(self, agent_id: str, name: str = "Ada", domain: str = "AI Security"):
        self.active_agents[agent_id] = {"name": name, "domain": domain}
        db = SessionLocal()
        try:
            run_research_cycle(db, agent_id, name, domain)
        finally:
            db.close()

    def trigger_tick(self, agent_id: str):
        db = SessionLocal()
        try:
            agent_info = self.active_agents.get(agent_id, {"name": "Ada", "domain": "AI Security"})
            return run_research_cycle(db, agent_id, agent_info["name"], agent_info["domain"])
        finally:
            db.close()

    async def start_background_loop(self):
        self.running = True
        print(f"[Scheduler] Background loop started. First delay: {settings.FIRST_CYCLE_DELAY_SECONDS}s, Interval: {settings.CYCLE_INTERVAL_SECONDS}s")
        
        db = SessionLocal()
        try:
            agents = restore_agents(db)
            for a in agents:
                self.active_agents[a.agent_id] = {"name": a.name, "domain": a.domain}
        finally:
            db.close()

        await asyncio.sleep(settings.FIRST_CYCLE_DELAY_SECONDS)

        while self.running:
            await asyncio.sleep(settings.CYCLE_INTERVAL_SECONDS)
            try:
                for agent_id, info in list(self.active_agents.items()):
                    db = SessionLocal()
                    try:
                        run_research_cycle(db, agent_id, info["name"], info["domain"])
                    finally:
                        db.close()
            except Exception as e:
                print(f"[Scheduler] Error during loop tick: {e}")

global_scheduler = AegisScheduler()
aegis_scheduler = global_scheduler
