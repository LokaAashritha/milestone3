from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SwipeX - Job & Data Intelligence Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = "sqlite:///./swipex_dev.db"
    
    # Redis Cache (Optional, falls back to in-memory cache if not available)
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 300  # 5 minutes default
    
    # Resume File Storage
    UPLOAD_DIR: str = "./uploads/resumes"
    MAX_RESUME_SIZE_MB: int = 10
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    model_config = SettingsConfigDict(case_sensitive=True, env_file=".env", extra="ignore")


settings = Settings()
