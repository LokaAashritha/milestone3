from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc

from app.api.deps import get_db, get_cache
from app.core.cache import CacheManager
from app.models.company import Company, CompanyType
from app.models.job import Job
from app.schemas.company import (
    CompanyCreate,
    CompanyOut,
    CompanyListResponse,
)
from app.schemas.job import CompanyDetailWithJobsOut, JobSummaryOut
from app.core.intelligence import (
    compute_job_freshness,
    compute_competition_level,
)
from app.api.v1.jobs import format_salary_range

router = APIRouter()


# ---------------------------------------------------------------------------
# CREATE COMPANY
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=CompanyOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Company",
)
def create_company(
    payload: CompanyCreate,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    """
    Creates the canonical company record owned by the Job Data service.

    Gateway companies are mapped to this record through:
        Gateway Company.job_data_company_id
    """

    existing = (
        db.query(Company)
        .filter(Company.slug == payload.slug)
        .first()
    )

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company with slug '{payload.slug}' already exists.",
        )

    company = Company(
        name=payload.name,
        slug=payload.slug,
        company_type=payload.company_type,
        is_newly_founded=payload.is_newly_founded,
        industry=payload.industry,
        headquarters=payload.headquarters,
        funding_stage=payload.funding_stage,
        logo_url=payload.logo_url,
        website=payload.website,
        description=payload.description,
        founded_year=payload.founded_year,
        employee_count_range=payload.employee_count_range,
    )

    db.add(company)
    db.commit()
    db.refresh(company)

    # Invalidate company-related caches.
    try:
        cache.clear()
    except Exception:
        pass

    return CompanyOut.model_validate(company)


# ---------------------------------------------------------------------------
# LIST COMPANIES
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=List[CompanyOut],
    summary="List Companies & Startups",
)
@router.get(
    "/list",
    response_model=CompanyListResponse,
    summary="List Companies with Pagination",
)
def get_companies(
    type: Optional[str] = Query(
        None,
        description="Filter by company type: MNC, Startup, Newly Founded",
    ),
    industry: Optional[str] = Query(
        None,
        description="Filter by industry (e.g. Fintech, AI, E-commerce)",
    ),
    newly_founded: Optional[bool] = Query(
        None,
        description="Filter specifically for newly founded startups",
    ),
    search: Optional[str] = Query(
        None,
        description="Search company name, description, or headquarters",
    ),
    page: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Items per page",
    ),
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    """
    Returns company listings supporting MNCs, high-growth startups,
    and early-stage AI startups.
    """

    cache_key = (
        f"companies:t={type}:ind={industry}:nf={newly_founded}:"
        f"q={search}:p={page}:ps={page_size}"
    )

    cached = cache.get(cache_key)

    if cached:
        return cached

    query = db.query(Company)

    if type:
        query = query.filter(
            Company.company_type.ilike(f"%{type.strip()}%")
        )

    if industry:
        query = query.filter(
            Company.industry.ilike(f"%{industry.strip()}%")
        )

    if newly_founded is not None:
        query = query.filter(
            Company.is_newly_founded == newly_founded
        )

    if search:
        term = f"%{search.strip()}%"

        query = query.filter(
            or_(
                Company.name.ilike(term),
                Company.description.ilike(term),
                Company.headquarters.ilike(term),
            )
        )

    query = query.order_by(Company.name.asc())

    companies = (
        query
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    results = [
        CompanyOut.model_validate(company)
        for company in companies
    ]

    serialized = [
        company.model_dump(mode="json")
        for company in results
    ]

    cache.set(
        cache_key,
        serialized,
        ttl=300,
    )

    return results


# ---------------------------------------------------------------------------
# COMPANY DETAIL
# ---------------------------------------------------------------------------

@router.get(
    "/{company_id}",
    response_model=CompanyDetailWithJobsOut,
    summary="Get Company Profile with Active Jobs",
)
def get_company_by_id(
    company_id: int,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    """
    Returns comprehensive company details along with all active
    job postings by this company.
    """

    cache_key = f"company_profile:{company_id}"

    cached = cache.get(cache_key)

    if cached:
        return cached

    company = (
        db.query(Company)
        .filter(Company.id == company_id)
        .first()
    )

    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {company_id} not found.",
        )

    active_jobs = (
        db.query(Job)
        .filter(
            Job.company_id == company_id,
            Job.is_active == True,
        )
        .order_by(desc(Job.posted_at))
        .all()
    )

    jobs_summary = []

    for job in active_jobs:
        freshness = compute_job_freshness(job.posted_at)
        comp_info = compute_competition_level(
            job.applicant_count
        )

        jobs_summary.append(
            JobSummaryOut(
                job_id=job.id,
                title=job.title,
                company=company.name,
                company_id=company.id,
                company_type=company.company_type,
                is_newly_founded=company.is_newly_founded,
                company_logo_url=company.logo_url,
                type=job.job_type.value,
                workplace_type=job.workplace_type.value,
                location=job.location,
                salary_range=format_salary_range(
                    job.salary_min,
                    job.salary_max,
                    job.salary_currency,
                    job.salary_period,
                ),
                salary_min=job.salary_min,
                salary_max=job.salary_max,
                salary_currency=job.salary_currency,
                skills=job.skills,
                required_skills=job.required_skills,
                keywords=job.keywords,
                experience_level=job.experience_level.value,
                competition_level=comp_info["competition_level"],
                applicant_count=job.applicant_count,
                is_fresher_friendly=job.is_fresher_friendly,
                posted_at=job.posted_at,
                freshness_label=freshness["freshness_label"],
                posted_days_ago=freshness["days_ago"],
                is_early_applicant=comp_info["is_early_applicant"],
            )
        )

    response_data = CompanyDetailWithJobsOut(
        id=company.id,
        name=company.name,
        slug=company.slug,
        company_type=company.company_type,
        is_newly_founded=company.is_newly_founded,
        industry=company.industry,
        headquarters=company.headquarters,
        funding_stage=company.funding_stage,
        logo_url=company.logo_url,
        website=company.website,
        description=company.description,
        founded_year=company.founded_year,
        employee_count_range=company.employee_count_range,
        created_at=company.created_at,
        active_jobs_count=len(jobs_summary),
        jobs=jobs_summary,
    )

    cache.set(
        cache_key,
        response_data.model_dump(mode="json"),
        ttl=300,
    )

    return response_data