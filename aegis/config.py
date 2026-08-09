import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "AEGIS Autonomous AI Software Engineering Engine"
    DEBUG: bool = True
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'data', 'aegis.db')}"
    
    # Scheduler & Execution Config
    FIRST_CYCLE_DELAY_SECONDS: int = 2
    CYCLE_INTERVAL_SECONDS: int = 40
    
    # Scoring Thresholds
    PUBLISH_THRESHOLD: float = 75.0
    HOLD_THRESHOLD: float = 60.0
    
    # LLM Provider Selection: 'deterministic', 'openai', 'groq', 'anthropic', 'gemini', 'watsonx'
    LLM_PROVIDER: str = "deterministic"
    LLM_MODEL: str = "gpt-4o-mini"
    
    # LLM API Keys
    OPENAI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    WATSONX_API_KEY: str = ""
    WATSONX_URL: str = ""
    WATSONX_PROJECT_ID: str = ""

    # Execution Sandbox Settings
    SANDBOX_TIMEOUT_SECONDS: int = 30
    SANDBOX_MAX_MEMORY_MB: int = 512
    SANDBOX_WORK_DIR: str = os.path.join(os.path.dirname(__file__), "sandbox_workspace")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
