import uuid
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from aegis.models import BeliefModel, now_utc

class BeliefEngine:
    """
    Extended Persistent Belief Engine:
    Maintains subject-level belief nodes with Bayesian confidence updates,
    evidence classifications (FACT, CLAIM, INFERENCE, UNCERTAINTY), supporting
    events, and contradicting events.
    """
    def record_or_update_belief(
        self,
        db: Session,
        agent_id: str,
        subject: str,
        statement: str,
        evidence_type: str = "INFERENCE",
        confidence: float = 0.85,
        supporting_event: Optional[str] = None,
        contradicting_event: Optional[str] = None
    ) -> BeliefModel:
        existing = db.query(BeliefModel).filter(
            BeliefModel.agent_id == agent_id,
            BeliefModel.subject == subject
        ).first()

        now = now_utc()

        if existing:
            # Parse event lists
            try:
                supports = json.loads(existing.supporting_events or "[]")
            except Exception:
                supports = []
            
            try:
                contradicts = json.loads(existing.contradicting_events or "[]")
            except Exception:
                contradicts = []

            if supporting_event:
                supports.append(supporting_event)
            if contradicting_event:
                contradicts.append(contradicting_event)

            # Bayesian-style weighted update
            if contradicting_event:
                # Reduce confidence
                new_conf = max(0.05, round(existing.confidence * 0.7, 2))
                existing.status = "CONTRADICTED"
            else:
                # Boost confidence with diminishing returns
                prior = existing.confidence
                likelihood = confidence
                bayes_conf = (prior * likelihood) / ((prior * likelihood) + ((1 - prior) * (1 - likelihood) + 1e-6))
                new_conf = min(0.99, max(0.1, round(bayes_conf, 2)))

            existing.statement = statement
            existing.evidence_type = evidence_type
            existing.confidence = new_conf
            existing.supporting_events = json.dumps(supports)
            existing.contradicting_events = json.dumps(contradicts)
            existing.updated_at = now
            db.commit()
            db.refresh(existing)
            return existing

        belief_id = f"blf-{uuid.uuid4().hex[:8]}"
        supports = [supporting_event] if supporting_event else []
        contradicts = [contradicting_event] if contradicting_event else []

        belief = BeliefModel(
            id=belief_id,
            agent_id=agent_id,
            subject=subject,
            statement=statement,
            evidence_type=evidence_type,
            confidence=confidence,
            status="ACTIVE",
            source_references="[]",
            supporting_events=json.dumps(supports),
            contradicting_events=json.dumps(contradicts),
            created_at=now,
            updated_at=now
        )
        db.add(belief)
        db.commit()
        db.refresh(belief)
        return belief

    def get_agent_beliefs(self, db: Session, agent_id: str) -> List[BeliefModel]:
        return db.query(BeliefModel).filter(BeliefModel.agent_id == agent_id).order_by(BeliefModel.updated_at.desc()).all()

belief_engine = BeliefEngine()
