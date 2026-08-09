import uuid
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from aegis.models import ApprovalGateModel, now_utc

HIGH_RISK_ACTIONS = [
    "DESTRUCTIVE_FILE_DELETE",
    "PRODUCTION_DEPLOY",
    "REMOTE_GIT_PUSH",
    "DATABASE_DROP",
    "DANGEROUS_SHELL_COMMAND"
]

class ApprovalGateManager:
    """
    Human Approval Gate Manager for intercepting sensitive high-risk operations
    until confirmed by human administrators via UI or REST API.
    """
    def check_approval(
        self,
        db: Session,
        project_id: str,
        action_type: str,
        description: str,
        command: Optional[str] = None
    ) -> Dict[str, Any]:
        if action_type not in HIGH_RISK_ACTIONS:
            return {"status": "APPROVED", "requires_approval": False}

        gate = ApprovalGateModel(
            id=f"ap-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            action_type=action_type,
            description=description,
            command=command,
            status="PENDING",
            requested_at=now_utc()
        )
        db.add(gate)
        db.commit()

        return {"status": "PENDING", "approval_id": gate.id, "requires_approval": True}

    def decide_approval(self, db: Session, approval_id: str, approve: bool) -> Dict[str, Any]:
        gate = db.query(ApprovalGateModel).filter(ApprovalGateModel.id == approval_id).first()
        if not gate:
            return {"status": "FAILED", "error": "Approval gate not found"}

        gate.status = "APPROVED" if approve else "REJECTED"
        gate.decided_at = now_utc()
        db.commit()

        return {"status": gate.status, "approval_id": approval_id}

approval_gate = ApprovalGateManager()
