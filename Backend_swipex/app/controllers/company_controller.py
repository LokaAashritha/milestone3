"""
app/controllers/company_controller.py

Company profile service:
    - GET    /api/v1/companies
    - GET    /api/v1/companies/{company_id}
    - POST   /api/v1/companies
    - PATCH  /api/v1/companies/{company_id}
    - DELETE /api/v1/companies/{company_id}

Integration:
    Gateway Company (UUID)
            ↓
    Job Data Company (INTEGER)
"""

import os
import re
import uuid
from typing import Optional

import requests

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Company, Job, User, UserRole
from app.schemas import (
    CompanyCreateRequest,
    CompanyUpdateRequest,
    CompanyOut,
    CompanyDetailOut,
)
from app.auth import (
    get_current_user,
    require_recruiter_or_admin,
    require_admin,
)
from app.utils import serialize_job


router = APIRouter()


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

JOB_DATA_SERVICE_URL = os.getenv(
    "JOB_DATA_SERVICE_URL",
    "http://localhost:8004/api/v1",
).rstrip("/")


# ---------------------------------------------------------------------------
# Job Data HTTP helpers
# ---------------------------------------------------------------------------

def _job_data_headers(user_id: uuid.UUID) -> dict:
    return {
        "X-User-ID": str(user_id),
        "Content-Type": "application/json",
    }


def _create_job_data_company(
    payload: CompanyCreateRequest,
    user_id: uuid.UUID,
) -> int:
    """
    Creates the canonical company record in Job Data.

    Job Data requires fields that Gateway does not currently store.
    Gateway therefore supplies deterministic defaults for those fields.
    """

    company_name = payload.name.strip()

    # Generate a unique, URL-safe slug.
    base_slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        company_name.lower(),
    ).strip("-")

    if not base_slug:
        base_slug = "company"

    slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"

    payload_data = payload.model_dump()

    # Gateway field → Job Data field mapping.
    job_data_payload = {
        "name": company_name,
        "slug": slug,
        "company_type": "Startup",
        "is_newly_founded": False,
        "industry": payload_data.get("industry") or "Technology",
        "headquarters": (
            payload_data.get("location")
            or "Not specified"
        ),
        "funding_stage": "Growth",
        "logo_url": payload_data.get("logo_url"),
        "website": payload_data.get("website"),
        "description": payload_data.get("about"),
        "founded_year": None,
        "employee_count_range": None,
    }

    try:
        response = requests.post(
            f"{JOB_DATA_SERVICE_URL}/companies",
            json=job_data_payload,
            headers=_job_data_headers(user_id),
            timeout=15,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Job Data service is unavailable: {exc}",
        )

    if response.status_code not in (200, 201):
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": "Job Data service rejected company creation.",
                "job_data_response": detail,
            },
        )

    try:
        data = response.json()
        job_data_company_id = int(data["id"])
    except (ValueError, TypeError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Invalid company response from Job Data service: {exc}",
        )

    return job_data_company_id


# ---------------------------------------------------------------------------
# LIST COMPANIES
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[CompanyOut],
    responses={
        200: {"description": "Company summaries"},
        401: {
            "model": dict,
            "description": "Authentication required",
        },
    },
    summary="List all companies (any authenticated user)",
)
def list_companies(
    industry: Optional[str] = Query(
        None,
        description="Filter by industry (partial match)",
    ),
    location: Optional[str] = Query(
        None,
        description="Filter by location (partial match)",
    ),
    keyword: Optional[str] = Query(
        None,
        description="Free-text search on company name",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(
            Company,
            func.count(Job.id).label("job_count"),
        )
        .outerjoin(Job)
        .group_by(Company.id)
    )

    if industry:
        query = query.filter(
            Company.industry.ilike(
                f"%{industry.strip()}%"
            )
        )

    if location:
        query = query.filter(
            Company.location.ilike(
                f"%{location.strip()}%"
            )
        )

    if keyword:
        query = query.filter(
            Company.name.ilike(
                f"%{keyword.strip()}%"
            )
        )

    results = query.order_by(
        Company.name.asc()
    ).all()

    output = []

    for company, job_count in results:
        item = CompanyOut.model_validate(company)
        item.job_count = job_count or 0
        output.append(item)

    return output


# ---------------------------------------------------------------------------
# COMPANY DETAIL
# ---------------------------------------------------------------------------

@router.get(
    "/{company_id}",
    response_model=CompanyDetailOut,
    responses={
        200: {
            "description": "Company profile with active jobs"
        },
        401: {
            "model": dict,
            "description": "Authentication required",
        },
        404: {
            "model": dict,
            "description": "Company not found",
        },
    },
    summary="Get a company's profile along with its active job listings",
)
def get_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = (
        db.query(Company)
        .options(joinedload(Company.jobs))
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    active_jobs = [
        job for job in company.jobs
        if job.is_active
    ]

    detail = CompanyDetailOut.model_validate(company)

    detail.job_count = len(active_jobs)

    detail.jobs = [
        serialize_job(job)
        for job in active_jobs
    ]

    return detail


# ---------------------------------------------------------------------------
# CREATE COMPANY
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=CompanyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company profile (Recruiter / Admin only)",
    dependencies=[
        Depends(require_recruiter_or_admin)
    ],
)
def create_company(
    payload: CompanyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Creates the company in both services.

    Flow:

        Gateway
            ↓
        Job Data POST /companies
            ↓
        integer Job Data company ID
            ↓
        Gateway stores job_data_company_id
    """

    # Prevent duplicate Gateway companies by name for the same recruiter.
    existing = (
        db.query(Company)
        .filter(
            func.lower(Company.name)
            == payload.name.strip().lower()
        )
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A company with this name already exists in Gateway.",
        )

    # Create canonical Job Data company first.
    job_data_company_id = _create_job_data_company(
        payload,
        current_user.id,
    )

    # Create Gateway company with the mapping.
    company_data = payload.model_dump()

    company = Company(
        **company_data,
        job_data_company_id=job_data_company_id,
    )

    db.add(company)

    try:
        db.commit()
        db.refresh(company)
    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Gateway company creation failed after the Job Data "
                f"company was created. Job Data company ID: "
                f"{job_data_company_id}. Error: {exc}"
            ),
        )

    # Attach recruiter to the newly-created company.
    if (
        current_user.role == UserRole.RECRUITER
        and current_user.company_id is None
    ):
        current_user.company_id = company.id
        db.commit()

    out = CompanyOut.model_validate(company)
    out.job_count = 0

    return out


# ---------------------------------------------------------------------------
# UPDATE COMPANY
# ---------------------------------------------------------------------------

@router.patch(
    "/{company_id}",
    response_model=CompanyOut,
    summary="Update a company profile (Recruiter / Admin only, owner-checked)",
    dependencies=[
        Depends(require_recruiter_or_admin)
    ],
)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    if (
        current_user.role == UserRole.RECRUITER
        and current_user.company_id != company.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Recruiters may only update their own "
                "company profile"
            ),
        )

    update_data = payload.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    job_count = (
        db.query(func.count(Job.id))
        .filter(Job.company_id == company.id)
        .scalar()
    )

    out = CompanyOut.model_validate(company)
    out.job_count = job_count or 0

    return out


# ---------------------------------------------------------------------------
# DELETE COMPANY
# ---------------------------------------------------------------------------

@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a company profile (Admin only)",
    dependencies=[
        Depends(require_admin)
    ],
)
def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    db.delete(company)
    db.commit()

    return None