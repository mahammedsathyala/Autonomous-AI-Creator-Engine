import uuid
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from aegis.models import AgentModel, now_utc

def create_agent(db: Session, name: str = "Ada", domain: str = "AI Security") -> AgentModel:
    clean_name = name.lower().replace(" ", "")
    clean_domain = domain.lower().replace(" ", "")[:4]
    agent_id = f"{clean_name}-{clean_domain}-{uuid.uuid4().hex[:4]}"

    agent = AgentModel(
        agent_id=agent_id,
        name=name,
        domain=domain,
        editorial_voice="Analytical, cybersecurity-focused, rigorous threat modeling",
        rejection_standards="Rejects non-technical hype, generic listicles, and clickbait",
        created_at=now_utc()
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent

def get_agent(db: Session, agent_id: str) -> Optional[AgentModel]:
    return db.query(AgentModel).filter(AgentModel.agent_id == agent_id).first()

def restore_agents(db: Session) -> List[AgentModel]:
    return db.query(AgentModel).all()
