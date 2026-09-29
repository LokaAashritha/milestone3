"""
app/controllers/job_controller.py

Job listing service:
    - GET    /api/v1/jobs            -> paginated, multi-parameter search/list
    - GET    /api/v1/jobs/{job_id}   -> job detail with dynamic metrics
    - POST   /api/v1/jobs            -> create (Recruiter / Admin only)
    - PATCH  /api/v1/jobs/{job_id}   -> update (Recruiter / Admin only, owner-checked)
    - DELETE /api/v1/jobs/{job_id}   -> delete (Recruiter / Admin only, owner-checked)

All GET endpoints require authentication (any role). Every job payload
returned to the client includes two fields computed on the fly:
    - posted_time:        human-readable relative time (e.g. "2 days ago")
    - competition_level:  Low / Medium / High derived from applicant_count
"""

import math
import uuid
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, and_, cast, String
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Job, Company, User, UserRole, JobType
from app.schemas import JobCreateRequest, JobUpdateRequest, JobOut, PaginatedJobsResponse
from app.auth import get_current_user, require_recruiter_or_admin
from app.utils import serialize_job

router = APIRouter()


@router.get(
    "",
    response_model=PaginatedJobsResponse,
    responses={
        200: {"description": "Paginated active job cards"},
        400: {"model": dict, "description": "Invalid query parameters"},
        401: {"model": dict, "description": "Authentication required"},
    },
    summary="List / search jobs with pagination and multi-parameter filters",
)
def list_jobs(
    page: int = Query(1, ge=1, description="Page number, starting at 1"),
    page_size: int = Query(20, ge=1, le=100, description="Number of results per page"),
    keyword: Optional[str] = Query(None, description="Free-text search across title and description"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    job_type: Optional[JobType] = Query(None, description="Filter by job type"),
    company_id: Optional[uuid.UUID] = Query(None, description="Filter by company"),
    skill: Optional[List[str]] = Query(None, description="Filter by one or more required skills"),
    salary_min: Optional[Decimal] = Query(None, ge=0, description="Minimum salary floor to filter on"),
    salary_max: Optional[Decimal] = Query(None, ge=0, description="Maximum salary ceiling to filter on"),
    sort_by: str = Query("posted_at", pattern="^(posted_at|salary_min|salary_max|applicant_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Job).options(joinedload(Job.company)).filter(Job.is_active == 1)

    if keyword:
        like_pattern = f"%{keyword.strip()}%"
        query = query.filter(
            or_(Job.title.ilike(like_pattern), Job.description.ilike(like_pattern))
        )

    if location:
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    if job_type:
        query = query.filter(Job.job_type == job_type)

    if company_id:
        query = query.filter(Job.company_id == company_id)

    if skill:
        # skills_required is a JSON array column; match jobs that contain
        # ANY of the requested skills (case-insensitive substring match on
        # the JSON-serialized column keeps this portable across DBs).
        skill_filters = [cast(Job.skills_required, String).ilike(f"%{s}%") for s in skill]
        query = query.filter(or_(*skill_filters))

    if salary_min is not None:
        query = query.filter(
            or_(Job.salary_max.is_(None), Job.salary_max >= salary_min)
        )

    if salary_max is not None:
        query = query.filter(
            or_(Job.salary_min.is_(None), Job.salary_min <= salary_max)
        )

    total = query.count()

    sort_column = getattr(Job, sort_by)
    sort_column = sort_column.desc() if sort_order == "desc" else sort_column.asc()
    query = query.order_by(sort_column)

    offset = (page - 1) * page_size
    jobs = query.offset(offset).limit(page_size).all()

    total_pages = math.ceil(total / page_size) if total > 0 else 0

    return PaginatedJobsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=[serialize_job(job) for job in jobs],
    )


@router.get(
    "/search",
    response_model=PaginatedJobsResponse,
    responses={
        200: {"description": "Filtered and paginated job cards"},
        400: {"model": dict, "description": "Invalid filter combination"},
        401: {"model": dict, "description": "Authentication required"},
    },
    summary="Search jobs with advanced frontend filter chips",
)
def search_jobs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = Query(None, description="Search title, description, or company name"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    salary_min: Optional[Decimal] = Query(None, ge=0),
    salary_max: Optional[Decimal] = Query(None, ge=0),
    job_type: Optional[JobType] = Query(None),
    experience_level: Optional[str] = Query(None),
    fresher_friendly: Optional[bool] = Query(None),
    low_competition: Optional[bool] = Query(None),
    recently_posted: Optional[bool] = Query(None, description="Only jobs created in the last 30 days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if salary_min is not None and salary_max is not None and salary_min > salary_max:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="salary_min cannot exceed salary_max")

    query = db.query(Job).options(joinedload(Job.company)).filter(Job.is_active == 1)
    if keyword:
        like_pattern = f"%{keyword.strip()}%"
        query = query.join(Company).filter(
            or_(Job.title.ilike(like_pattern), Job.description.ilike(like_pattern), Company.name.ilike(like_pattern))
        )
    if location:
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))
    if salary_min is not None:
        query = query.filter(or_(Job.salary_max.is_(None), Job.salary_max >= salary_min))
    if salary_max is not None:
        query = query.filter(or_(Job.salary_min.is_(None), Job.salary_min <= salary_max))
    if job_type is not None:
        query = query.filter(Job.job_type == job_type)
    if experience_level:
        query = query.filter(Job.experience_level.ilike(experience_level.strip()))
    if fresher_friendly is not None:
        query = query.filter(Job.fresher_friendly == fresher_friendly)
    if low_competition is not None:
        query = query.filter(Job.low_competition == low_competition)
    if recently_posted:
        query = query.filter(Job.created_at >= datetime.now(timezone.utc) - timedelta(days=30))

    total = query.count()
    jobs = query.order_by(Job.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return PaginatedJobsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total else 0,
        results=[serialize_job(job) for job in jobs],
    )


@router.get(
    "/{job_id}",
    response_model=JobOut,
    responses={
        200: {"description": "Job card"},
        401: {"model": dict, "description": "Authentication required"},
        404: {"model": dict, "description": "Job not found"},
    },
    summary="Get a single job's details with dynamic intelligence metrics",
)
def get_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.id == job_id)
        .first()
    )
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    return serialize_job(job)


@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting (Recruiter / Admin only)",
    dependencies=[Depends(require_recruiter_or_admin)],
)
def create_job(
    payload: JobCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == payload.company_id).first()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    # Recruiters may only post jobs for the company they belong to.
    # Admins may post for any company.
    if current_user.role == UserRole.RECRUITER and current_user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiters may only create jobs for their own company",
        )

    job = Job(
        company_id=payload.company_id,
        posted_by=current_user.id,
        title=payload.title,
        description=payload.description,
        location=payload.location,
        job_type=payload.job_type,
        experience_level=payload.experience_level,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        skills_required=payload.skills_required or [],
        fresher_friendly=payload.fresher_friendly,
        low_competition=payload.low_competition,
        applicant_count=0,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job.id).first()

    return serialize_job(job)


@router.patch(
    "/{job_id}",
    response_model=JobOut,
    summary="Update an existing job posting (Recruiter / Admin only, owner-checked)",
    dependencies=[Depends(require_recruiter_or_admin)],
)
def update_job(
    job_id: uuid.UUID,
    payload: JobUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).options(joinedload(Job.company)).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if current_user.role == UserRole.RECRUITER and current_user.company_id != job.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiters may only update jobs belonging to their own company",
        )

    update_data = payload.model_dump(exclude_unset=True)
    if "is_active" in update_data:
        update_data["is_active"] = 1 if update_data["is_active"] else 0

    for field, value in update_data.items():
        setattr(job, field, value)

    db.commit()
    db.refresh(job)

    return serialize_job(job)


@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job posting (Recruiter / Admin only, owner-checked)",
    dependencies=[Depends(require_recruiter_or_admin)],
)
def delete_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

    if current_user.role == UserRole.RECRUITER and current_user.company_id != job.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiters may only delete jobs belonging to their own company",
        )

    db.delete(job)
    db.commit()
    return None
