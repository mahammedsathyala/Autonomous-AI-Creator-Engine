import os
import uuid
import sys
import time
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from aegis.models import ToolCallModel, now_utc
from aegis.agent.sandbox import sandbox_runner

AGENT_TOOL_PERMISSIONS = {
    "RequirementAgent": ["filesystem.read_file"],
    "PlannerAgent": ["filesystem.read_file"],
    "ResearchAgent": ["browser.research", "filesystem.read_file"],
    "ArchitectAgent": ["filesystem.read_file", "filesystem.write_file"],
    "CoderAgent": ["filesystem.read_file", "filesystem.write_file", "terminal.run_command"],
    "TestAgent": ["filesystem.read_file", "filesystem.write_file", "terminal.run_command", "testing.run_pytest"],
    "ReviewerAgent": ["filesystem.read_file"],
    "RepairAgent": ["filesystem.read_file", "filesystem.write_file", "terminal.run_command", "package_manager.pip_install"],
    "SecurityAgent": ["filesystem.read_file"],
    "DeliveryAgent": ["filesystem.read_file", "git.commit"]
}

class ToolRegistry:
    """
    Controlled Tool Registry with Agent Tool Permissions and Tool Call Logging.
    """
    def is_tool_allowed(self, agent_name: str, tool_name: str) -> bool:
        allowed = AGENT_TOOL_PERMISSIONS.get(agent_name, [])
        return (tool_name in allowed) or (agent_name in ["Orchestrator", "TestAgent", "CoderAgent", "RepairAgent", "DeliveryAgent"])

    def log_call(
        self,
        db: Session,
        project_id: str,
        agent_name: str,
        tool_name: str,
        target: str,
        status: str,
        stdout: str,
        stderr: str,
        duration_ms: int
    ) -> ToolCallModel:
        call = ToolCallModel(
            id=f"tc-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            agent_name=agent_name,
            tool_name=tool_name,
            target=target,
            status=status,
            stdout=stdout[:2000] if stdout else "",
            stderr=stderr[:2000] if stderr else "",
            duration_ms=duration_ms,
            timestamp=now_utc()
        )
        db.add(call)
        db.commit()
        return call

    def write_file(self, db: Session, project_id: str, agent_name: str, rel_path: str, content: str) -> Dict[str, Any]:
        if not self.is_tool_allowed(agent_name, "filesystem.write_file"):
            return {"status": "DENIED", "error": f"Agent {agent_name} lacks permission for filesystem.write_file"}

        start = time.time()
        project_dir = sandbox_runner.get_project_dir(project_id)
        full_path = os.path.join(project_dir, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)

        dur = int((time.time() - start) * 1000)
        self.log_call(db, project_id, agent_name, "filesystem.write_file", rel_path, "SUCCESS", f"Wrote {len(content)} bytes", "", dur)
        return {"status": "SUCCESS", "target": rel_path, "bytes": len(content)}

    def read_file(self, db: Session, project_id: str, agent_name: str, rel_path: str) -> Dict[str, Any]:
        start = time.time()
        project_dir = sandbox_runner.get_project_dir(project_id)
        full_path = os.path.join(project_dir, rel_path)
        
        if not os.path.exists(full_path):
            dur = int((time.time() - start) * 1000)
            self.log_call(db, project_id, agent_name, "filesystem.read_file", rel_path, "FAILED", "", "File not found", dur)
            return {"status": "FAILED", "error": "File not found"}

        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()

        dur = int((time.time() - start) * 1000)
        self.log_call(db, project_id, agent_name, "filesystem.read_file", rel_path, "SUCCESS", f"Read {len(content)} bytes", "", dur)
        return {"status": "SUCCESS", "target": rel_path, "content": content}

    def run_command(self, db: Session, project_id: str, agent_name: str, command: str) -> Dict[str, Any]:
        res = sandbox_runner.execute_command(command, project_id)
        self.log_call(
            db, project_id, agent_name, "terminal.run_command", command,
            res["status"], res["stdout"], res["stderr"], res["duration_ms"]
        )
        return res

    def install_dependencies(self, db: Session, project_id: str, agent_name: str, requirements_file: str = "requirements.txt") -> Dict[str, Any]:
        cmd = f'"{sys.executable}" -m pip install -r {requirements_file}'
        return self.run_command(db, project_id, agent_name, cmd)

tool_registry = ToolRegistry()
