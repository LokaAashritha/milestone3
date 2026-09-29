from pathlib import Path

from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APP_DIR = BASE_DIR / "app"


class Settings(BaseModel):
    PROJECT_NAME: str = "SwipeX Career Intelligence Service"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"

    UPLOAD_DIR: Path = BASE_DIR / "storage" / "resumes"
    MAX_FILE_SIZE_BYTES: int = 10 * 1024 * 1024
    ALLOWED_EXTENSIONS: set[str] = {".pdf", ".docx", ".txt"}
    ALLOWED_MIME_TYPES: set[str] = {
        "application/pdf",
        "text/plain",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/msword",
        "application/octet-stream",
    }

    DATA_DIR: Path = APP_DIR / "data"
    SEED_JOBS_FILE: Path = APP_DIR / "data" / "seed_jobs.json"

    REQUIRED_SKILLS_WEIGHT: float = 0.70
    KEYWORD_OVERLAP_WEIGHT: float = 0.30
    GENERATED_BY_TAG: str = "blended-v2"

    CHROMADB_HOST: str = "chromadb"
    CHROMADB_PORT: int = 8001
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    BLENDED_KEYWORD_WEIGHT: float = 0.50
    BLENDED_SEMANTIC_WEIGHT: float = 0.50
    ATS_TARGET_THRESHOLD: float = 80.0


settings = Settings()

settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)

