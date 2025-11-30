"""
Configuration settings for Med Procedure
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # App Configuration
    app_name: str = "Med Procedure"
    app_version: str = "1.0.0"
    log_level: str = "INFO"
    
    # Groq Configuration (replaces OpenAI)
    groq_api_key: Optional[str] = None
    
    # Phidata Configuration (optional)
    phi_api_key: Optional[str] = None
    
    # Google Search API Configuration
    serpapi_api_key: Optional[str] = None
    
    # LangSmith Configuration
    langchain_api_key: Optional[str] = None
    langchain_tracing_v2: bool = True
    langchain_project: str = "Med-Procedure"
    
    # Redis Configuration
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    
    # Agent Configuration
    max_iterations: int = 50
    memory_bank_size: int = 1000
    context_compaction_threshold: float = 0.8
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env that aren't in the model


settings = Settings()

