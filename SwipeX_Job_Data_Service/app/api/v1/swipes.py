from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.api.deps import get_db, get_current_user_id
from app.models.job import Job
from app.models.company import Company
from app.models.swipe import Swipe, SwipeDirection, SwipeActionType
from app.schemas.swipe import (
    SwipeCreate, SwipeOut, SwipeHistoryItem, SwipeSummaryOut
)
from app.schemas.job import JobSummaryOut
from app.api.v1.jobs import format_salary_range

router = APIRouter()


@router.post("", response_model=SwipeOut, status_code=status.HTTP_201_CREATED, summary="Record a User Swipe")
def record_swipe(
    swipe_in: SwipeCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Records a swipe action on a job card:
    - **direction**: 'right' (apply/save) or 'left' (skip)
    - **action_type**: optional 'apply', 'save', or 'skip' (defaults smartly based on direction)
    """
    user_id = swipe_in.user_id if swipe_in.user_id and swipe_in.user_id != "demo-user-1" else current_user_id

    # Validate that the job exists
    job = db.query(Job).filter(Job.id == swipe_in.job_id).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {swipe_in.job_id} does not exist."
        )

    # Determine default action_type if not provided
    action_type = swipe_in.action_type
    if not action_type:
        if swipe_in.direction == SwipeDirection.RIGHT:
            action_type = SwipeActionType.APPLY
        else:
            action_type = SwipeActionType.SKIP

    # Check for existing swipe for this user and job (Update if exists, or Create new)
    existing_swipe = (
        db.query(Swipe)
        .filter(Swipe.user_id == user_id, Swipe.job_id == swipe_in.job_id)
        .first()
    )

    if existing_swipe:
        existing_swipe.direction = swipe_in.direction
        existing_swipe.action_type = action_type
        existing_swipe.notes = swipe_in.notes
        existing_swipe.created_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_swipe)
        swipe_obj = existing_swipe
    else:
        swipe_obj = Swipe(
            user_id=user_id,
            job_id=swipe_in.job_id,
            direction=swipe_in.direction,
            action_type=action_type,
            notes=swipe_in.notes,
            created_at=datetime.utcnow()
        )
        db.add(swipe_obj)
        
        # If right swipe with apply action, increment applicant count
        if swipe_in.direction == SwipeDirection.RIGHT and action_type == SwipeActionType.APPLY:
            job.applicant_count += 1
            
        db.commit()
        db.refresh(swipe_obj)

    return SwipeOut(
        swipe_id=swipe_obj.id,
        user_id=swipe_obj.user_id,
        job_id=swipe_obj.job_id,
        direction=swipe_obj.direction,
        action_type=swipe_obj.action_type,
        swiped_at=swipe_obj.created_at,
        message="Swipe recorded successfully"
    )


@router.get("/history", response_model=List[SwipeHistoryItem], summary="Get User Swipe History (Frozen Contract API)")
def get_swipe_history(
    direction: Optional[SwipeDirection] = Query(None, description="Filter history by swipe direction (right or left)"),
    action_type: Optional[SwipeActionType] = Query(None, description="Filter by action: apply, save, skip"),
    user_id: Optional[str] = Query(None, description="Target user ID (defaults to current user)"),
    limit: int = Query(50, ge=1, le=200, description="Max history items"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns swipe history matching SRS 7.2 contract:
    `GET /api/v1/swipes/history` -> 200 `[ { job_id, direction, swiped_at } ]`
    Also embeds rich job summary for dashboard consumption.
    """
    target_user = user_id or current_user_id

    query = db.query(Swipe).filter(Swipe.user_id == target_user)

    if direction:
        query = query.filter(Swipe.direction == direction)
    if action_type:
        query = query.filter(Swipe.action_type == action_type)

    swipes = query.order_by(desc(Swipe.created_at)).limit(limit).all()

    results = []
    for s in swipes:
        job_summary = None
        if s.job:
            j = s.job
            job_summary = JobSummaryOut(
                job_id=j.id,
                title=j.title,
                company=j.company.name if j.company else "Unknown",
                company_id=j.company_id,
                company_type=j.company.company_type if j.company else "Startup",
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
                competition_level=j.competition_level.value,
                applicant_count=j.applicant_count,
                is_fresher_friendly=j.is_fresher_friendly,
                posted_at=j.posted_at
            )

        results.append(
            SwipeHistoryItem(
                job_id=s.job_id,
                direction=s.direction,
                action_type=s.action_type,
                swiped_at=s.created_at,
                job=job_summary
            )
        )

    return results


@router.get("/summary", response_model=SwipeSummaryOut, summary="Get Swipe Metrics Summary")
def get_swipe_summary(
    user_id: Optional[str] = Query(None, description="Target user ID (defaults to current user)"),
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    Returns high-level statistics for dashboard widgets:
    total swipes, right swipes, left swipes, applied count, saved count, skipped count.
    """
    target_user = user_id or current_user_id

    user_swipes = db.query(Swipe).filter(Swipe.user_id == target_user).all()

    total = len(user_swipes)
    right_swipes = sum(1 for s in user_swipes if s.direction == SwipeDirection.RIGHT)
    left_swipes = sum(1 for s in user_swipes if s.direction == SwipeDirection.LEFT)
    applied = sum(1 for s in user_swipes if s.action_type == SwipeActionType.APPLY)
    saved = sum(1 for s in user_swipes if s.action_type == SwipeActionType.SAVE)
    skipped = sum(1 for s in user_swipes if s.action_type == SwipeActionType.SKIP)

    return SwipeSummaryOut(
        user_id=target_user,
        total_swipes=total,
        right_swipes=right_swipes,
        left_swipes=left_swipes,
        applied_count=applied,
        saved_count=saved,
        skipped_count=skipped
    )
