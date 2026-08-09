import uuid
import json
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from aegis.models import (
    MemoryEpisodicModel,
    MemorySemanticModel,
    MemoryProjectModel,
    MemoryFailureModel,
    now_utc
)

class ShortTermMemoryBuffer:
    """In-memory transient context for active task execution."""
    def __init__(self):
        self.objective: str = ""
        self.active_task: Optional[str] = None
        self.current_agent: Optional[str] = None
        self.recent_errors: List[str] = []

    def set_context(self, objective: str, active_task: str, current_agent: str):
        self.objective = objective
        self.active_task = active_task
        self.current_agent = current_agent

    def add_error(self, error_msg: str):
        self.recent_errors.append(error_msg[:500])

    def clear(self):
        self.objective = ""
        self.active_task = None
        self.current_agent = None
        self.recent_errors = []

class MultiLayerMemorySystem:
    """
    Multi-layer persistent memory manager handling Episodic, Semantic,
    Project, and Failure Memory with error signature matching.
    """
    def __init__(self):
        self.short_term = ShortTermMemoryBuffer()

    def extract_error_signature(self, stderr: str) -> str:
        if not stderr:
            return "UnknownError"
        match = re.search(r'([A-Za-z0-9_]+Error:[^\n]+)', stderr)
        if match:
            return match.group(1).strip()
        lines = [l.strip() for l in stderr.splitlines() if l.strip()]
        return lines[-1][:80] if lines else "ExecutionFailure"

    def record_failure_solution(
        self,
        db: Session,
        project_id: str,
        stderr: str,
        solution_description: str
    ) -> MemoryFailureModel:
        sig = self.extract_error_signature(stderr)
        existing = db.query(MemoryFailureModel).filter(MemoryFailureModel.error_signature == sig).first()
        if existing:
            existing.solution = solution_description
            existing.success_count += 1
            db.commit()
            db.refresh(existing)
            return existing

        failure = MemoryFailureModel(
            id=f"mf-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            error_signature=sig,
            error_context=stderr[:1000],
            solution=solution_description,
            success_count=1,
            created_at=now_utc()
        )
        db.add(failure)
        db.commit()
        db.refresh(failure)
        return failure

    def find_failure_solution(self, db: Session, stderr: str) -> Optional[str]:
        sig = self.extract_error_signature(stderr)
        match = db.query(MemoryFailureModel).filter(MemoryFailureModel.error_signature == sig).first()
        if match:
            return match.solution
        
        all_failures = db.query(MemoryFailureModel).all()
        for f in all_failures:
            if f.error_signature in stderr or sig in f.error_context:
                return f.solution
        return None

    def record_episodic(
        self,
        db: Session,
        project_id: str,
        task_code: str,
        action: str,
        result: str,
        status: str = "SUCCESS"
    ) -> MemoryEpisodicModel:
        item = MemoryEpisodicModel(
            id=f"ep-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            task_code=task_code,
            action=action,
            result=result[:2000],
            status=status,
            timestamp=now_utc()
        )
        db.add(item)
        db.commit()
        return item

    def save_project_memory(self, db: Session, project_id: str, key: str, value: Any) -> MemoryProjectModel:
        val_json = json.dumps(value)
        existing = db.query(MemoryProjectModel).filter(
            MemoryProjectModel.project_id == project_id,
            MemoryProjectModel.key == key
        ).first()

        if existing:
            existing.value_json = val_json
            existing.updated_at = now_utc()
            db.commit()
            db.refresh(existing)
            return existing

        mem = MemoryProjectModel(
            id=f"pm-{uuid.uuid4().hex[:8]}",
            project_id=project_id,
            key=key,
            value_json=val_json,
            updated_at=now_utc()
        )
        db.add(mem)
        db.commit()
        db.refresh(mem)
        return mem

    def get_project_memory(self, db: Session, project_id: str, key: str) -> Optional[Any]:
        mem = db.query(MemoryProjectModel).filter(
            MemoryProjectModel.project_id == project_id,
            MemoryProjectModel.key == key
        ).first()
        if mem:
            try:
                return json.loads(mem.value_json)
            except Exception:
                return mem.value_json
        return None

memory_system = MultiLayerMemorySystem()
