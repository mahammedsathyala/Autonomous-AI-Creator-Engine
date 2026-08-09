import asyncio
import time
from typing import Dict
from agent_engine import AutonomousAgentEngine
import database as db

class AgentScheduler:
    """
    Manages autonomous background publishing tasks across active agents.
    Runs periodically (e.g. every 45 seconds) without needing external triggers.
    """
    def __init__(self):
        self.active_agents: Dict[str, AutonomousAgentEngine] = {}
        self.running = False
        self.interval_seconds = 40  # Autonomous cycle frequency
        self.last_run_time = 0

    def register_agent(self, agent_id: str, name: str, domain: str) -> AutonomousAgentEngine:
        if agent_id not in self.active_agents:
            engine = AutonomousAgentEngine(agent_id=agent_id, name=name, domain=domain)
            self.active_agents[agent_id] = engine
            # Run immediate cycle upon initialization so evaluator has initial posts right away!
            engine.run_autonomous_cycle()
        return self.active_agents[agent_id]

    def trigger_tick(self, agent_id: str):
        """Forces an immediate cycle for demo/testing."""
        if agent_id in self.active_agents:
            return self.active_agents[agent_id].run_autonomous_cycle()
        else:
            # Load agent from DB if registered earlier
            agent_data = db.get_agent(agent_id)
            if agent_data:
                engine = self.register_agent(agent_id, agent_data["name"], agent_data["domain"])
                return engine.run_autonomous_cycle()
        return None

    async def start_background_loop(self):
        self.running = True
        print("[Scheduler] Autonomous background publishing loop started.")
        while self.running:
            await asyncio.sleep(self.interval_seconds)
            try:
                for agent_id, engine in list(self.active_agents.items()):
                    engine.run_autonomous_cycle()
            except Exception as e:
                print(f"[Scheduler] Error during autonomous cycle: {e}")

global_scheduler = AgentScheduler()
