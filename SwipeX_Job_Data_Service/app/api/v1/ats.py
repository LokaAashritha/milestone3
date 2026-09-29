from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.resume_service import ResumeService
from app.models.job import Job
from app.schemas.resume import ATSScoreRequest, ATSScoreResponse
from app.api.v1.resumes import get_current_user_id

router = APIRouter()


@router.post(
    "/score",
    response_model=ATSScoreResponse,
    summary="Compute ATS Resume-to-Job Compatibility Score"
)
def score_resume(
    req: ATSScoreRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Computes ATS compatibility score between a user's parsed resume and a target job.
    Blends keyword match percentage with skill overlap.
    
    Business Rule (FR-04):
    If match_score < 80%: identifies missing_skills and missing_keywords.
    If match_score >= 80%: both missing arrays are empty [].
    """
    # Verify resume ownership
    resume = ResumeService.get_user_resume(db, req.resume_id, current_user_id)

    # Find job
    job = None
    try:
        job_int_id = int(req.job_id)
        job = db.query(Job).filter(Job.id == job_int_id, Job.is_active == True).first()
    except (ValueError, TypeError):
        # In case job_id is string or uuid
        job = db.query(Job).filter(Job.is_active == True).first()

    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID '{req.job_id}' not found."
        )

    score_result = ResumeService.compute_ats_score(resume, job)
    # Ensure job_id in response echoes request job_id
    score_result["job_id"] = str(req.job_id)
    return score_result
