from datetime import datetime
from typing import List, Optional, Union
from pydantic import BaseModel, Field, ConfigDict


class ResumeBase(BaseModel):
    file_name: str
    file_type: str
    version_number: int = 1
    is_active_version: bool = True
    parsed_status: str = "pending"


class ResumeUploadOut(BaseModel):
    id: str
    user_id: str
    file_name: str
    file_type: str
    version_number: int
    is_active_version: bool
    parsed_status: str
    parsed_text: Optional[str] = None
    extracted_skills: Optional[List[str]] = None
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailOut(ResumeUploadOut):
    file_size: Optional[int] = 0
    parsed_at: Optional[datetime] = None


class ResumeParseTriggerRequest(BaseModel):
    parsed_text: str = Field(..., description="Clean plain text extracted from the resume file")
    extracted_skills: List[str] = Field(..., description="List of recognized skills (NER/dictionary)")


class ATSScoreRequest(BaseModel):
    resume_id: str = Field(..., description="UUID of the parsed resume")
    job_id: Union[str, int] = Field(..., description="Target Job ID")


class ATSScoreResponse(BaseModel):
    resume_id: str
    job_id: str
    match_score: float = Field(..., ge=0.0, le=100.0, description="Blended match percentage between 0 and 100")
    missing_skills: List[str] = Field(default_factory=list, description="Populated only when match_score < 80")
    missing_keywords: List[str] = Field(default_factory=list, description="Populated only when match_score < 80")
    scored_at: str
