from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.job import JobSummaryOut


class SavedJobCreate(BaseModel):
    job_id: int
    notes: Optional[str] = None
    user_id: Optional[str] = "demo-user-1"


class SavedJobOut(BaseModel):
    id: int
    user_id: str
    job_id: int
    notes: Optional[str] = None
    saved_at: datetime
    message: str = "Job saved successfully"

    model_config = ConfigDict(from_attributes=True)


class SavedJobItem(BaseModel):
    id: int
    user_id: str
    job_id: int
    notes: Optional[str] = None
    saved_at: datetime
    job: Optional[JobSummaryOut] = None

    model_config = ConfigDict(from_attributes=True)
