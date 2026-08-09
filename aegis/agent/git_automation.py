import os
import uuid
from typing import Dict, Any
from sqlalchemy.orm import Session
from aegis.agent.tools import tool_registry

class GitAutomation:
    """Automates Git repository initialization, branch setup, and conventional commits."""
    def init_repo(self, db: Session, project_id: str) -> Dict[str, Any]:
        tool_registry.run_command(db, project_id, "GitAutomation", "git init")
        tool_registry.run_command(db, project_id, "GitAutomation", "git branch -M main")
        return {"status": "SUCCESS", "message": "Git repository initialized."}

    def commit_changes(self, db: Session, project_id: str, message: str) -> Dict[str, Any]:
        tool_registry.run_command(db, project_id, "GitAutomation", "git add .")
        res = tool_registry.run_command(db, project_id, "GitAutomation", f'git commit -m "{message}"')
        return res

    def get_status(self, db: Session, project_id: str) -> Dict[str, Any]:
        return tool_registry.run_command(db, project_id, "GitAutomation", "git status")

git_automation = GitAutomation()
