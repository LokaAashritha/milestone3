import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, desc, asc, String, cast

from app.api.deps import get_db, get_cache
from app.core.cache import CacheManager
from app.models.company import Company, CompanyType
from app.models.job import (
    Job, JobType, WorkplaceType, ExperienceLevel, CompetitionLevel
)
from app.schemas.job import (
    JobSummaryOut,
    JobDetailOut,
    JobListResponse,
    JobCreate,
)
from app.schemas.company import CompanyOut
from app.core.intelligence import compute_job_freshness, compute_competition_level

router = APIRouter()


def format_salary_range(sal_min: Optional[int], sal_max: Optional[int], currency: str = "INR", period: str = "Per Annum") -> str:
    """Formats salary integer values into clean human-readable text."""
    if not sal_min and not sal_max:
        return "Not Disclosed"
    
    symbol = "₹" if currency == "INR" else "$"
    suffix = " PA" if period == "Per Annum" else " /mo"

    def format_num(val: int) -> str:
        if currency == "INR":
            if val >= 100000:
                lakhs = val / 100000
                return f"{lakhs:.1f} LPA".replace(".0 LPA", " LPA")
            return f"{val:,}"
        else:
            if val >= 1000:
                return f"{val//1000}k"
            return f"{val:,}"

    if sal_min and sal_max:
        if currency == "INR" and period == "Per Annum":
            return f"{symbol}{format_num(sal_min)} - {symbol}{format_num(sal_max)}"
        return f"{symbol}{format_num(sal_min)} - {symbol}{format_num(sal_max)}{suffix}"
    elif sal_min:
        return f"From {symbol}{format_num(sal_min)}{suffix}"
    else:
        return f"Up to {symbol}{format_num(sal_max)}{suffix}"


def serialize_job_summary(job: Job) -> JobSummaryOut:
    freshness = compute_job_freshness(job.posted_at)
    comp_info = compute_competition_level(job.applicant_count)

    return JobSummaryOut(
        job_id=job.id,
        title=job.title,
        company=job.company.name if job.company else "Unknown",
        company_id=job.company_id,
        company_type=job.company.company_type if job.company else CompanyType.STARTUP,
        is_newly_founded=job.company.is_newly_founded if job.company else False,
        company_logo_url=job.company.logo_url if job.company else None,
        type=job.job_type.value,
        workplace_type=job.workplace_type.value,
        location=job.location,
        salary_range=format_salary_range(job.salary_min, job.salary_max, job.salary_currency, job.salary_period),
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
        is_early_applicant=comp_info["is_early_applicant"]
    )


@router.get("", response_model=List[JobSummaryOut], summary="List Jobs (Frozen Contract API)")
@router.get("/list", response_model=JobListResponse, summary="List Jobs (With Pagination Metadata)")
def get_jobs(
    type: Optional[str] = Query(None, description="Filter by Company Type (MNC, Startup, Newly Founded) or Job Type (Full-time, Internship)"),
    location: Optional[str] = Query(None, description="Filter by city/location substring (e.g. Bengaluru, Pune, Remote)"),
    remote: Optional[bool] = Query(None, description="True for remote-only roles"),
    salary_min: Optional[int] = Query(None, description="Minimum salary threshold"),
    salary_max: Optional[int] = Query(None, description="Maximum salary threshold"),
    skills: Optional[str] = Query(None, description="Comma-separated skill names (e.g. Python,React,SQL)"),
    experience_level: Optional[str] = Query(None, description="Experience level: Fresher, Entry-level, Mid-level, Senior"),
    competition_level: Optional[str] = Query(None, description="Competition level: Low, Medium, High"),
    fresher_friendly: Optional[bool] = Query(None, description="Filter for fresher-friendly positions"),
    newly_founded: Optional[bool] = Query(None, description="Filter jobs from newly founded startups"),
    search: Optional[str] = Query(None, description="Keyword search across title, description, company"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    sort_by: Optional[str] = Query("posted_at_desc", description="Sort: posted_at_desc, salary_desc, competition_asc"),
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache)
):
    """
    Returns filtered job listings matching SRS Interface Contracts with Milestone 2 intelligence indicators.
    """
    cache_key = f"jobs:t={type}:loc={location}:rem={remote}:smin={salary_min}:smax={salary_max}:sk={skills}:exp={experience_level}:comp={competition_level}:ff={fresher_friendly}:nf={newly_founded}:q={search}:p={page}:ps={page_size}:sort={sort_by}"
    cached_data = cache.get(cache_key)
    if cached_data:
        return cached_data

    query = db.query(Job).join(Company).filter(Job.is_active == True)

    if type:
        type_clean = type.strip()
        query = query.filter(
            or_(
                cast(Company.company_type, String).ilike(f"%{type_clean}%"),
                cast(Job.job_type, String).ilike(f"%{type_clean}%")
            )
        )

    if location:
        query = query.filter(
            or_(
                Job.location.ilike(f"%{location.strip()}%"),
                Company.headquarters.ilike(f"%{location.strip()}%")
            )
        )

    if remote is not None:
        if remote is True:
            query = query.filter(Job.workplace_type == WorkplaceType.REMOTE)
        else:
            query = query.filter(Job.workplace_type != WorkplaceType.REMOTE)

    if salary_min is not None:
        query = query.filter(Job.salary_max >= salary_min)
    if salary_max is not None:
        query = query.filter(Job.salary_min <= salary_max)

    if skills:
        skill_list = [s.strip().lower() for s in skills.split(",") if s.strip()]
        for skill in skill_list:
            query = query.filter(Job._skills.ilike(f"%{skill}%"))

    if experience_level:
        query = query.filter(cast(Job.experience_level, String).ilike(f"%{experience_level.strip()}%"))

    if competition_level:
        query = query.filter(cast(Job.competition_level, String).ilike(f"%{competition_level.strip()}%"))

    if fresher_friendly is not None:
        query = query.filter(Job.is_fresher_friendly == fresher_friendly)

    if newly_founded is not None:
        query = query.filter(Company.is_newly_founded == newly_founded)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Job.title.ilike(search_term),
                Job.description.ilike(search_term),
                Job.role_category.ilike(search_term),
                Company.name.ilike(search_term)
            )
        )

    if sort_by == "salary_desc":
        query = query.order_by(desc(Job.salary_max), desc(Job.posted_at))
    elif sort_by == "competition_asc":
        query = query.order_by(asc(Job.applicant_count), desc(Job.posted_at))
    else:
        query = query.order_by(desc(Job.posted_at))

    jobs_slice = query.offset((page - 1) * page_size).limit(page_size).all()
    formatted_jobs = [serialize_job_summary(j) for j in jobs_slice]

    serialized = [j.model_dump(mode="json") for j in formatted_jobs]
    cache.set(cache_key, serialized, ttl=300)

    return formatted_jobs


@router.get("/search", response_model=List[JobSummaryOut], summary="Smart Full-Text Search & Multi-Criteria Filtering (FR-03)")
def search_jobs(
    q: Optional[str] = Query(None, description="Free text keyword search query (e.g., 'Python FastAPI', 'Swiggy', 'ML Intern')"),
    location: Optional[str] = Query(None, description="Target city or 'Remote'"),
    job_type: Optional[str] = Query(None, description="Full-time, Internship, Contract"),
    experience_level: Optional[str] = Query(None, description="Fresher, Entry-level, Mid-level, Senior"),
    salary_min: Optional[int] = Query(None, description="Minimum salary bracket"),
    salary_max: Optional[int] = Query(None, description="Maximum salary bracket"),
    skills: Optional[str] = Query(None, description="Required skills (comma-separated)"),
    company_type: Optional[str] = Query(None, description="MNC, Startup, Newly Founded"),
    is_fresh_only: Optional[bool] = Query(None, description="Only jobs posted within last 3 days"),
    low_competition_only: Optional[bool] = Query(None, description="Only low competition jobs (< 25 applicants)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(25, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """
    Dedicated Milestone 2 Search API (FR-03).
    Performs fast multi-attribute keyword search across job title, description,
    responsibilities, requirements, skills array, and company details.
    """
    query = db.query(Job).join(Company).filter(Job.is_active == True)

    if q:
        terms = [t.strip() for t in q.split() if len(t.strip()) > 1]
        for term in terms:
            like_pat = f"%{term}%"
            query = query.filter(
                or_(
                    Job.title.ilike(like_pat),
                    Job.description.ilike(like_pat),
                    Job.role_category.ilike(like_pat),
                    Job._skills.ilike(like_pat),
                    Company.name.ilike(like_pat),
                    Company.industry.ilike(like_pat)
                )
            )

    if location:
        query = query.filter(Job.location.ilike(f"%{location.strip()}%"))

    if job_type:
        query = query.filter(cast(Job.job_type, String).ilike(f"%{job_type.strip()}%"))

    if experience_level:
        query = query.filter(cast(Job.experience_level, String).ilike(f"%{experience_level.strip()}%"))

    if salary_min is not None:
        query = query.filter(Job.salary_max >= salary_min)

    if salary_max is not None:
        query = query.filter(Job.salary_min <= salary_max)

    if skills:
        skill_items = [s.strip().lower() for s in skills.split(",") if s.strip()]
        for skill in skill_items:
            query = query.filter(Job._skills.ilike(f"%{skill}%"))

    if company_type:
        query = query.filter(cast(Company.company_type, String).ilike(f"%{company_type.strip()}%"))

    if low_competition_only is True:
        query = query.filter(Job.applicant_count < 25)

    query = query.order_by(desc(Job.posted_at))

    results = query.offset((page - 1) * page_size).limit(page_size).all()
    formatted = [serialize_job_summary(j) for j in results]

    # If is_fresh_only is True, filter in memory based on intelligence rule
    if is_fresh_only is True:
        formatted = [j for j in formatted if j.freshness_label in ["Just Posted", "Recently Posted"]]

    return formatted

@router.post(
    "",
    response_model=JobDetailOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create Job"
)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache),
):
    """
    Creates the canonical Job Data record.

    Job Data owns the AI/ML-facing job record and generates
    the integer job ID used by the AIML service.
    """

    company = (
        db.query(Company)
        .filter(Company.id == payload.company_id)
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ID {payload.company_id} not found."
        )

    job = Job(
        company_id=payload.company_id,
        title=payload.title,
        role_category=payload.role_category,
        description=payload.description,
        responsibilities=payload.responsibilities,
        requirements=payload.requirements,
        job_type=payload.job_type,
        workplace_type=payload.workplace_type,
        location=payload.location,
        salary_min=payload.salary_min,
        salary_max=payload.salary_max,
        salary_currency=payload.salary_currency,
        salary_period=payload.salary_period,
        experience_level=payload.experience_level,
        experience_years_min=payload.experience_years_min,
        experience_years_max=payload.experience_years_max,
        competition_level=payload.competition_level,
        applicant_count=payload.applicant_count,
        is_fresher_friendly=payload.is_fresher_friendly,
        is_active=payload.is_active,
        expires_at=payload.expires_at,
    )

    job.skills = payload.skills
    job.required_skills = payload.required_skills
    job.keywords = payload.keywords

    db.add(job)
    db.commit()
    db.refresh(job)

    # Prevent stale cached job-list/detail responses.
    try:
        cache.delete(f"job_detail:{job.id}")
    except Exception:
        pass

    freshness = compute_job_freshness(job.posted_at)
    comp_info = compute_competition_level(job.applicant_count)

    company_out = CompanyOut.model_validate(job.company) if job.company else None

    return JobDetailOut(
        id=job.id,
        job_id=job.id,
        title=job.title,
        company=company_out,
        role_category=job.role_category,
        description=job.description,
        responsibilities=job.responsibilities,
        requirements=job.requirements,
        skills=job.skills,
        required_skills=job.required_skills,
        keywords=job.keywords,
        job_type=job.job_type,
        workplace_type=job.workplace_type,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        salary_range=format_salary_range(
            job.salary_min,
            job.salary_max,
            job.salary_currency,
            job.salary_period,
        ),
        experience_level=job.experience_level,
        experience_years_min=job.experience_years_min,
        experience_years_max=job.experience_years_max,
        competition_level=comp_info["competition_level"],
        applicant_count=job.applicant_count,
        is_fresher_friendly=job.is_fresher_friendly,
        is_active=job.is_active,
        posted_at=job.posted_at,
        expires_at=job.expires_at,
        created_at=job.posted_at,
        freshness_label=freshness["freshness_label"],
        posted_days_ago=freshness["days_ago"],
        is_early_applicant=comp_info["is_early_applicant"],
        competition_score=comp_info["competition_score"],
    )


@router.get("/{job_id}", response_model=JobDetailOut, summary="Get Job Detail by ID")
def get_job_by_id(
    job_id: int,
    db: Session = Depends(get_db),
    cache: CacheManager = Depends(get_cache)
):
    """
    Returns full job details including company profile, description,
    requirements, compensation metadata, freshness indicators, and competition score.
    """
    cache_key = f"job_detail:{job_id}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    job = db.query(Job).filter(Job.id == job_id, Job.is_active == True).first()
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job with ID {job_id} not found."
        )

    company_out = CompanyOut.model_validate(job.company) if job.company else None
    freshness = compute_job_freshness(job.posted_at)
    comp_info = compute_competition_level(job.applicant_count)

    detail = JobDetailOut(
        id=job.id,
        job_id=job.id,
        title=job.title,
        company=company_out,
        role_category=job.role_category,
        description=job.description,
        responsibilities=job.responsibilities,
        requirements=job.requirements,
        skills=job.skills,
        required_skills=job.required_skills,
        keywords=job.keywords,
        job_type=job.job_type,
        workplace_type=job.workplace_type,
        location=job.location,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        salary_currency=job.salary_currency,
        salary_period=job.salary_period,
        salary_range=format_salary_range(job.salary_min, job.salary_max, job.salary_currency, job.salary_period),
        experience_level=job.experience_level,
        experience_years_min=job.experience_years_min,
        experience_years_max=job.experience_years_max,
        competition_level=comp_info["competition_level"],
        applicant_count=job.applicant_count,
        is_fresher_friendly=job.is_fresher_friendly,
        is_active=job.is_active,
        posted_at=job.posted_at,
        expires_at=job.expires_at,
        created_at=job.posted_at,
        freshness_label=freshness["freshness_label"],
        posted_days_ago=freshness["days_ago"],
        is_early_applicant=comp_info["is_early_applicant"],
        competition_score=comp_info["competition_score"]
    )

    cache.set(cache_key, detail.model_dump(mode="json"), ttl=600)
    return detail
