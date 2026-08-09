import uuid
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from aegis.models import BeliefModel, now_utc

class BeliefEngine:
    """
    Persistent Belief Engine:
    Maintains subject-level beliefs with evidence classifications:
    - FACT: Verified CVEs, code patches, advisories.
    - CLAIM: Vendor announcements, author assertions.
    - INFERENCE: Deductions drawn by AEGIS persona.
    - UNCERTAINTY: Open questions, unverified threats.
    """
    def record_or_update_belief(
        self,
        db: Session,
        agent_id: str,
        subject: str,
        statement: str,
        evidence_type: str = "INFERENCE",
        confidence: float = 0.85
    ) -> BeliefModel:
        # Check existing belief for subject
        existing = db.query(BeliefModel).filter(
            BeliefModel.agent_id == agent_id,
            BeliefModel.subject == subject
        ).first()

        if existing:
            existing.statement = statement
            existing.evidence_type = evidence_type
            existing.confidence = min(1.0, max(0.1, (existing.confidence + confidence) / 2.0))
            existing.updated_at = now_utc()
            db.commit()
            db.refresh(existing)
            return existing

        belief_id = f"blf-{uuid.uuid4().hex[:8]}"
        belief = BeliefModel(
            id=belief_id,
            agent_id=agent_id,
            subject=subject,
            statement=statement,
            evidence_type=evidence_type,
            confidence=confidence,
            updated_at=now_utc()
        )
        db.add(belief)
        db.commit()
        db.refresh(belief)
        return belief

    def get_agent_beliefs(self, db: Session, agent_id: str) -> List[BeliefModel]:
        return db.query(BeliefModel).filter(BeliefModel.agent_id == agent_id).order_by(BeliefModel.updated_at.desc()).all()

belief_engine = BeliefEngine()
