import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user
from app.database import get_db
from app.models import Job, SavedJob, User
from app.utils import serialize_job

router = APIRouter()


class SavedJobCreateRequest(BaseModel):
    job_id: uuid.UUID
    notes: str = Field(default="", max_length=2000)


def serialize_saved_job(saved_job: SavedJob) -> dict:
    return {
        **serialize_job(saved_job.job),
        "job_id": str(saved_job.job_id),
        "notes": saved_job.notes or "",
        "saved_at": saved_job.created_at,
    }


@router.post("", status_code=status.HTTP_201_CREATED)
def save_job(
    payload: SavedJobCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == payload.job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    saved_job = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == payload.job_id,
    ).first()
    if saved_job is None:
        saved_job = SavedJob(user_id=current_user.id, job_id=payload.job_id, notes=payload.notes)
        db.add(saved_job)
    else:
        saved_job.notes = payload.notes

    db.commit()
    saved_job = db.query(SavedJob).options(joinedload(SavedJob.job)).filter(
        SavedJob.id == saved_job.id
    ).first()
    return serialize_saved_job(saved_job)


@router.get("")
def list_saved_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_jobs = db.query(SavedJob).options(joinedload(SavedJob.job)).filter(
        SavedJob.user_id == current_user.id
    ).order_by(SavedJob.created_at.desc()).all()
    return {
        "total": len(saved_jobs),
        "results": [serialize_saved_job(saved_job) for saved_job in saved_jobs],
    }


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    saved_job = db.query(SavedJob).filter(
        SavedJob.user_id == current_user.id,
        SavedJob.job_id == job_id,
    ).first()
    if saved_job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved job not found")

    db.delete(saved_job)
    db.commit()
    return None