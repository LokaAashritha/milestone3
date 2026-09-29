"""
app/controllers/swipe_controller.py

Swipe engine service:
    - POST /api/v1/swipes             -> record apply / save / skip (Job Seeker only)
    - GET  /api/v1/swipes             -> list the current user's swipe history
    - GET  /api/v1/swipes/{swipe_id}  -> get a single swipe record
    - DELETE /api/v1/swipes/{swipe_id} -> undo a swipe

Business rules:
    - A user may only have ONE swipe row per job (enforced by a DB
      UniqueConstraint on (user_id, job_id)). Swiping again on the same job
      UPDATES the existing swipe's action rather than creating a duplicate.
    - Job.applicant_count is incremented exactly once the first time a user
      applies to a job, and decremented if an "apply" swipe is later changed
      to something else or deleted, so the count always reflects the number
      of distinct users currently applied.
"""

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Swipe, Job, User, SwipeAction
from app.schemas import SwipeCreateRequest, SwipeOut, SwipeListResponse
from app.auth import get_current_user, require_job_seeker

router = APIRouter()


@router.post(
    "",
    response_model=SwipeOut,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": dict, "description": "Inactive job"},
        401: {"model": dict, "description": "Authentication required"},
        403: {"model": dict, "description": "Job Seeker role required"},
        404: {"model": dict, "description": "Job not found"},
        409: {"model": dict, "description": "Concurrent duplicate swipe"},
    },
    summary="Record a swipe action (apply / save / skip) on a job — Job Seeker only",
    dependencies=[Depends(require_job_seeker)],
)
def create_swipe(
    payload: SwipeCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id).with_for_update().first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")
    if not job.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This job is no longer accepting applicants")

    existing = (
        db.query(Swipe)
        .filter(Swipe.user_id == current_user.id, Swipe.job_id == payload.job_id)
        .with_for_update()
        .first()
    )

    if existing is not None:
        previous_action = existing.action
        existing.action = payload.action

        # Reconcile applicant_count when the action transitions to/from "apply".
        if previous_action != SwipeAction.APPLY and payload.action == SwipeAction.APPLY:
            job.applicant_count = (job.applicant_count or 0) + 1
        elif previous_action == SwipeAction.APPLY and payload.action != SwipeAction.APPLY:
            job.applicant_count = max((job.applicant_count or 0) - 1, 0)

        db.commit()
        db.refresh(existing)
        return SwipeOut.model_validate(existing)

    swipe = Swipe(
        user_id=current_user.id,
        job_id=payload.job_id,
        action=payload.action,
    )
    db.add(swipe)

    if payload.action == SwipeAction.APPLY:
        job.applicant_count = (job.applicant_count or 0) + 1

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A swipe for this job by this user already exists",
        )

    db.refresh(swipe)
    return SwipeOut.model_validate(swipe)


@router.get(
    "",
    response_model=SwipeListResponse,
    summary="List the current user's swipe history, optionally filtered by action",
)
def list_swipes(
    action: Optional[SwipeAction] = Query(None, description="Filter by apply / save / skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Swipe).filter(Swipe.user_id == current_user.id)
    if action:
        query = query.filter(Swipe.action == action)

    swipes = query.order_by(Swipe.created_at.desc()).all()
    return SwipeListResponse(total=len(swipes), results=[SwipeOut.model_validate(s) for s in swipes])


@router.get(
    "/{swipe_id}",
    response_model=SwipeOut,
    summary="Get a single swipe record belonging to the current user",
)
def get_swipe(
    swipe_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    swipe = (
        db.query(Swipe)
        .filter(Swipe.id == swipe_id, Swipe.user_id == current_user.id)
        .first()
    )
    if swipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swipe not found")
    return SwipeOut.model_validate(swipe)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"model": dict, "description": "Authentication required"},
        403: {"model": dict, "description": "Job Seeker role required"},
        404: {"model": dict, "description": "Swipe not found"},
    },
    summary="Undo/delete the current user's swipe for a job",
    dependencies=[Depends(require_job_seeker)],
)
def delete_swipe(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    swipe = (
        db.query(Swipe)
        .filter(Swipe.job_id == job_id, Swipe.user_id == current_user.id)
        .with_for_update()
        .first()
    )
    if swipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Swipe not found")

    if swipe.action == SwipeAction.APPLY:
        job = db.query(Job).filter(Job.id == swipe.job_id).with_for_update().first()
        if job is not None:
            job.applicant_count = max((job.applicant_count or 0) - 1, 0)

    db.delete(swipe)
    db.commit()
    return None
