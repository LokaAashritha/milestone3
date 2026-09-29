from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Header, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.resume_service import ResumeService
from app.models.resume import Resume
from app.schemas.resume import (
    ResumeUploadOut, ResumeDetailOut, ResumeParseTriggerRequest
)

router = APIRouter()

# Default test user ID matching Aashritha's M3 contract
DEFAULT_USER_ID = "4f9c2e3d-1111-4444-8888-123456789abc"


def get_current_user_id(
    x_user_id: Optional[str] = Header(None, description="Current authenticated Job Seeker user_id"),
    user_id: Optional[str] = Query(None, description="Optional user_id query parameter")
) -> str:
    """Helper to extract user_id from headers/query or fall back to default job seeker."""
    return x_user_id or user_id or DEFAULT_USER_ID


@router.post(
    "/upload",
    response_model=ResumeUploadOut,
    status_code=status.HTTP_201_CREATED,
    summary="Upload Resume (PDF/DOCX, max 10MB)"
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (.pdf or .docx)"),
    user_id: Optional[str] = Form(None, description="Job seeker user ID"),
    is_active_version: bool = Form(True, description="Mark as default/active version"),
    x_user_id: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF or DOCX resume file (up to 10MB).
    Creates a new version row without overwriting previous versions (FR-01).
    Validates format (400) and size (413).
    """
    active_user_id = user_id or x_user_id or DEFAULT_USER_ID
    content = await file.read()

    resume = ResumeService.create_resume_version(
        db=db,
        user_id=active_user_id,
        filename=file.filename,
        content=content,
        is_active=is_active_version
    )
    return resume


@router.get(
    "",
    response_model=List[ResumeUploadOut],
    summary="List Current User's Resume Versions"
)
def list_resumes(
    active_only: bool = Query(False, description="Filter to only the active/default resume version"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retrieves all resume versions uploaded by the authenticated user, newest first.
    Strictly isolated per user.
    """
    return ResumeService.list_user_resumes(db, current_user_id, active_only=active_only)


@router.get(
    "/{id}",
    response_model=ResumeDetailOut,
    summary="Get Resume Details & Parsed Skills"
)
def get_resume(
    id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Retrieves detailed metadata for a specific resume, including parsed_text and extracted_skills.
    Returns 404 if not found or owned by another user.
    """
    return ResumeService.get_user_resume(db, id, current_user_id)


@router.post(
    "/{id}/parse",
    response_model=ResumeDetailOut,
    summary="Trigger Resume Parsing & Skill Extraction"
)
def trigger_parse(
    id: str,
    payload: ResumeParseTriggerRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Callback endpoint used by Intern 4's extraction module to store parsed_text,
    extracted_skills, and populate normalized ResumeSkill records.
    """
    return ResumeService.save_parsed_results(
        db=db,
        resume_id=id,
        user_id=current_user_id,
        parsed_text=payload.parsed_text,
        extracted_skills=payload.extracted_skills
    )


@router.patch(
    "/{id}/activate",
    response_model=ResumeUploadOut,
    summary="Set Resume Version as Active"
)
def activate_resume(
    id: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Marks the specified resume version as the default/active version for job recommendations."""
    return ResumeService.set_active_version(db, current_user_id, id)
