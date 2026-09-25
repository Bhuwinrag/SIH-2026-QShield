from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl
from typing import List, Union

class Settings(BaseSettings):
    PROJECT_NAME: str = "Q-SHIELD"
    API_V1_STR: str = "/api/v1"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/qshield"
    
    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Quantum Simulator
    DEFAULT_SHOTS: int = 1000
    NOISE_ENABLED: bool = True
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

settings = Settings()
