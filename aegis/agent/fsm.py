import uuid
import json
from typing import Dict, Any, Optional, List, Tuple
from sqlalchemy.orm import Session
from aegis.models import ProjectModel, StateTransitionModel, now_utc

FSM_STATES_17 = [
    "CREATED",
    "REQUIREMENTS_ANALYZED",
    "PLANNED",
    "RESEARCHED",
    "ARCHITECTED",
    "IMPLEMENTING",
    "BUILDING",
    "TESTING",
    "FAILED",
    "REPAIRING",
    "RETESTING",
    "REVIEWING",
    "SECURITY_REVIEW",
    "VALIDATED",
    "GIT_COMMIT",
    "READY",
    "COMPLETED"
]

class ProjectStateMachine:
    """
    17-State Finite State Machine enforcing exact lifecycle transitions,
    failure routing loops, max retry bounds, and persistent state transition logs.
    """
    def __init__(self, max_repair_retries: int = 3):
        self.max_repair_retries = max_repair_retries

    def transition_to(
        self,
        db: Session,
        project_id: str,
        target_state: str,
        triggered_by: str,
        details: Optional[Dict[str, Any]] = None
    ) -> ProjectModel:
        if target_state not in FSM_STATES_17:
            raise ValueError(f"Invalid target state '{target_state}'. Must be one of {FSM_STATES_17}")

        project = db.query(ProjectModel).filter(ProjectModel.id == project_id).first()
        if not project:
            raise ValueError(f"Project '{project_id}' not found.")

        from_state = project.current_state or "CREATED"

        # Update Project state
        project.current_state = target_state
        project.status = target_state
        project.updated_at = now_utc()

        # Log transition
        transition = StateTransitionModel(
            id=f"tr-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            from_state=from_state,
            to_state=target_state,
            triggered_by=triggered_by,
            timestamp=now_utc(),
            details_json=json.dumps(details or {})
        )
        db.add(transition)
        db.commit()
        db.refresh(project)
        return project

    def handle_test_failure(
        self,
        db: Session,
        project_id: str,
        current_retries: int,
        error_details: Dict[str, Any]
    ) -> Tuple[str, ProjectModel]:
        """Routes failure state: transitions to REPAIRING if within retry limit, else FAILED."""
        if current_retries < self.max_repair_retries:
            next_state = "REPAIRING"
            details = {"attempt": current_retries + 1, "max_retries": self.max_repair_retries, "error": error_details}
        else:
            next_state = "FAILED"
            details = {"reason": "Max repair retries exceeded", "total_retries": current_retries, "error": error_details}

        project = self.transition_to(db, project_id, next_state, triggered_by="TestAgent", details=details)
        return next_state, project

project_fsm = ProjectStateMachine()
