import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AEGIS Cyber Intelligence Autonomous Creator"
    DEBUG: bool = True
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'data', 'aegis.db')}"
    
    # Scheduler & Execution Config
    FIRST_CYCLE_DELAY_SECONDS: int = 2
    CYCLE_INTERVAL_SECONDS: int = 40
    
    # Scoring Thresholds
    PUBLISH_THRESHOLD: float = 75.0
    HOLD_THRESHOLD: float = 60.0
    
    # Scoring Dimension Weights (Total = 1.0)
    WEIGHT_SECURITY_IMPACT: float = 0.30
    WEIGHT_NOVELTY: float = 0.20
    WEIGHT_EVIDENCE_QUALITY: float = 0.20
    WEIGHT_AI_RELEVANCE: float = 0.20
    WEIGHT_RESEARCH_VALUE: float = 0.10
    
    # LLM API Keys (optional; fallback engine used if unconfigured)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
