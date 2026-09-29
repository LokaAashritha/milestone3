from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user_id
from app.models.job import Job
from app.models.saved_job import SavedJob
from app.schemas.saved_job import SavedJobCreate, SavedJobOut, SavedJobItem
from app.schemas.job import JobSummaryOut
from app.core.intelligence import compute_job_freshness, compute_competition_level
from app.api.v1.jobs import format_salary_range

router = APIRouter()


@router.post("", response_model=SavedJobOut, status_code=status.HTTP_201_CREATED, summary="Save or Bookmark a Job")
def save_job(
    saved_in: SavedJobCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Saves a job to the candidate's bookmarked list.
    """
    user_id = saved_in.user_id if saved_in.user_id and saved_in.user_id != "demo-user-1" else current_user_id

    # Verify job exists
    job = db.query(Job).filter(Job.id == saved_in.job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {saved_in.job_id} not found."
        )

    # Check if already saved
    existing = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == user_id, SavedJob.job_id == saved_in.job_id)
        .first()
    )
    if existing:
        if saved_in.notes:
            existing.notes = saved_in.notes
            db.commit()
            db.refresh(existing)
        return SavedJobOut(
            id=existing.id,
            user_id=existing.user_id,
            job_id=existing.job_id,
            notes=existing.notes,
            saved_at=existing.saved_at,
            message="Job was already saved. Updated notes."
        )

    saved_obj = SavedJob(
        user_id=user_id,
        job_id=saved_in.job_id,
        notes=saved_in.notes
    )
    db.add(saved_obj)
    db.commit()
    db.refresh(saved_obj)

    return SavedJobOut(
        id=saved_obj.id,
        user_id=saved_obj.user_id,
        job_id=saved_obj.job_id,
        notes=saved_obj.notes,
        saved_at=saved_obj.saved_at,
        message="Job saved successfully"
    )


@router.get("", response_model=List[SavedJobItem], summary="Get User Saved Jobs")
def get_saved_jobs(
    user_id: Optional[str] = Query(None, description="Target user ID (defaults to current user)"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns list of saved jobs with complete job card summaries for the candidate.
    """
    target_user = user_id or current_user_id

    saved_list = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == target_user)
        .order_by(desc(SavedJob.saved_at))
        .all()
    )

    items = []
    for s in saved_list:
        job_summary = None
        if s.job:
            j = s.job
            freshness = compute_job_freshness(j.posted_at)
            comp_info = compute_competition_level(j.applicant_count)

            job_summary = JobSummaryOut(
                job_id=j.id,
                title=j.title,
                company=j.company.name if j.company else "Unknown",
                company_id=j.company_id,
                company_type=j.company.company_type if j.company else "Startup",
                is_newly_founded=j.company.is_newly_founded if j.company else False,
                company_logo_url=j.company.logo_url if j.company else None,
                type=j.job_type.value,
                workplace_type=j.workplace_type.value,
                location=j.location,
                salary_range=format_salary_range(j.salary_min, j.salary_max, j.salary_currency, j.salary_period),
                salary_min=j.salary_min,
                salary_max=j.salary_max,
                salary_currency=j.salary_currency,
                skills=j.skills,
                experience_level=j.experience_level.value,
                competition_level=comp_info["competition_level"],
                applicant_count=j.applicant_count,
                is_fresher_friendly=j.is_fresher_friendly,
                posted_at=j.posted_at,
                freshness_label=freshness["freshness_label"],
                posted_days_ago=freshness["days_ago"],
                is_early_applicant=comp_info["is_early_applicant"]
            )

        items.append(
            SavedJobItem(
                id=s.id,
                user_id=s.user_id,
                job_id=s.job_id,
                notes=s.notes,
                saved_at=s.saved_at,
                job=job_summary
            )
        )

    return items


@router.delete("/{job_id}", status_code=status.HTTP_200_OK, summary="Remove a Saved Job")
def delete_saved_job(
    job_id: int,
    user_id: Optional[str] = Query(None, description="Target user ID"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Removes a job from user's saved list.
    """
    target_user = user_id or current_user_id

    saved_entry = (
        db.query(SavedJob)
        .filter(SavedJob.user_id == target_user, SavedJob.job_id == job_id)
        .first()
    )
    if not saved_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} is not in user's saved list."
        )

    db.delete(saved_entry)
    db.commit()

    return {"status": "success", "message": f"Job {job_id} removed from saved list."}
