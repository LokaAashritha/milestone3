"""
app/controllers/company_controller.py

Company profile service:
    - GET    /api/v1/companies              -> list companies (authenticated)
    - GET    /api/v1/companies/{company_id} -> company detail + its jobs
    - POST   /api/v1/companies              -> create (Recruiter / Admin only)
    - PATCH  /api/v1/companies/{company_id} -> update (Recruiter / Admin only, owner-checked)
    - DELETE /api/v1/companies/{company_id} -> delete (Admin only)
"""

import uuid
from typing import Optional

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
from app.auth import get_current_user, require_recruiter_or_admin, require_admin
from app.utils import serialize_job

router = APIRouter()


@router.get(
    "",
    response_model=list[CompanyOut],
    responses={
        200: {"description": "Company summaries"},
        401: {"model": dict, "description": "Authentication required"},
    },
    summary="List all companies (any authenticated user)",
)
def list_companies(
    industry: Optional[str] = Query(None, description="Filter by industry (partial match)"),
    location: Optional[str] = Query(None, description="Filter by location (partial match)"),
    keyword: Optional[str] = Query(None, description="Free-text search on company name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Company, func.count(Job.id).label("job_count")).outerjoin(Job).group_by(Company.id)

    if industry:
        query = query.filter(Company.industry.ilike(f"%{industry.strip()}%"))
    if location:
        query = query.filter(Company.location.ilike(f"%{location.strip()}%"))
    if keyword:
        query = query.filter(Company.name.ilike(f"%{keyword.strip()}%"))

    results = query.order_by(Company.name.asc()).all()

    output = []
    for company, job_count in results:
        item = CompanyOut.model_validate(company)
        item.job_count = job_count or 0
        output.append(item)
    return output


@router.get(
    "/{company_id}",
    response_model=CompanyDetailOut,
    responses={
        200: {"description": "Company profile with active jobs"},
        401: {"model": dict, "description": "Authentication required"},
        404: {"model": dict, "description": "Company not found"},
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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    active_jobs = [j for j in company.jobs if j.is_active]

    detail = CompanyDetailOut.model_validate(company)
    detail.job_count = len(active_jobs)
    detail.jobs = [serialize_job(j) for j in active_jobs]
    return detail


@router.post(
    "",
    response_model=CompanyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new company profile (Recruiter / Admin only)",
    dependencies=[Depends(require_recruiter_or_admin)],
)
def create_company(
    payload: CompanyCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = Company(**payload.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)

    # If the creator is a recruiter without a company yet, attach them to it.
    if current_user.role == UserRole.RECRUITER and current_user.company_id is None:
        current_user.company_id = company.id
        db.commit()

    out = CompanyOut.model_validate(company)
    out.job_count = 0
    return out


@router.patch(
    "/{company_id}",
    response_model=CompanyOut,
    summary="Update a company profile (Recruiter / Admin only, owner-checked)",
    dependencies=[Depends(require_recruiter_or_admin)],
)
def update_company(
    company_id: uuid.UUID,
    payload: CompanyUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    if current_user.role == UserRole.RECRUITER and current_user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Recruiters may only update their own company profile",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)

    db.commit()
    db.refresh(company)

    job_count = db.query(func.count(Job.id)).filter(Job.company_id == company.id).scalar()
    out = CompanyOut.model_validate(company)
    out.job_count = job_count or 0
    return out


@router.delete(
    "/{company_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a company profile (Admin only)",
    dependencies=[Depends(require_admin)],
)
def delete_company(
    company_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    company = db.query(Company).filter(Company.id == company_id).first()
    if company is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company not found")

    db.delete(company)
    db.commit()
    return None
