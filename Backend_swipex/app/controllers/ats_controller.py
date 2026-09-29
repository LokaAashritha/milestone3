import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Resume, Job, User
from app.auth import get_current_user

from app.services.mock_ats_engine import generate_ats_score, generate_ai_suggestions

# --- Schemas ---

class ATSScoreRequest(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID

class ATSScoreResponse(BaseModel):
    match_score: float
    summary: Optional[str] = None
    missing_skills: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None

class AISuggestionItem(BaseModel):
    category: str
    suggestion: str

class AISuggestionsResponse(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID
    overall_feedback: str
    suggestions: List[AISuggestionItem]


router = APIRouter()


# --- Endpoint 1: ATS Scoring ---

@router.post(
    "/score", 
    response_model=ATSScoreResponse, 
    status_code=status.HTTP_200_OK
)
def calculate_ats_score(
    payload: ATSScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # RBAC Policy Check
    if hasattr(current_user, "role") and current_user.role not in ["candidate", "job_seeker", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Role insufficient for ATS scoring",
        )

    # 1. Verify Resume Ownership & Existence
    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # 2. Verify Job Existence
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # 3. Call ATS Engine Service
    resume_text = resume.parsed_text or ""
    resume_skills = getattr(resume, "extracted_skills", []) or []
    job_description = getattr(job, "description", "")
    job_skills = getattr(job, "skills_required", []) or []

    engine_result = generate_ats_score(
        resume_text=resume_text,
        resume_skills=resume_skills,
        job_description=job_description,
        job_skills=job_skills,
    )

    match_score = engine_result.get("match_score", 0.0)

    # 4. Enforce SRS Threshold Rules (< 80 rule)
    if match_score < 80.0:
        missing_skills = engine_result.get("missing_skills", [])
        missing_keywords = engine_result.get("missing_keywords", [])
    else:
        missing_skills = None
        missing_keywords = None

    # 5. Return structured response payload
    return ATSScoreResponse(
        match_score=match_score,
        summary=engine_result.get("summary", "Match score generated based on skill requirement overlap."),
        missing_skills=missing_skills,
        missing_keywords=missing_keywords,
    )


# --- Endpoint 2: Task 5.1 AI Suggestions Endpoint ---

@router.post(
    "/suggestions",
    response_model=AISuggestionsResponse,
    status_code=status.HTTP_200_OK
)
def get_ai_suggestions(
    payload: ATSScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # RBAC Policy Check
    if hasattr(current_user, "role") and current_user.role not in ["candidate", "job_seeker", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Role insufficient for AI suggestions",
        )

    # 1. Verify Resume Ownership & Existence
    resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )

    # 2. Verify Job Existence
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # 3. Get ATS evaluation data to generate targeted suggestions
    resume_text = resume.parsed_text or ""
    resume_skills = getattr(resume, "extracted_skills", []) or []
    job_description = getattr(job, "description", "")
    job_skills = getattr(job, "skills_required", []) or []

    ats_data = generate_ats_score(
        resume_text=resume_text,
        resume_skills=resume_skills,
        job_description=job_description,
        job_skills=job_skills,
    )

    # 4. Generate AI Suggestions via engine service
    suggestions_data = generate_ai_suggestions(
        resume_skills=resume_skills,
        job_skills=job_skills,
        missing_skills=ats_data.get("missing_skills", []),
        missing_keywords=ats_data.get("missing_keywords", []),
    )

    return AISuggestionsResponse(
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        overall_feedback=suggestions_data.get("overall_feedback", "Focus on aligning your key technical skills with the job post."),
        suggestions=suggestions_data.get("suggestions", []),
    )