"""
app/controllers/job_controller.py

Job listing and recruiter job-posting service.

Gateway owns:
    - Authentication / RBAC
    - Gateway PostgreSQL job record
    - Gateway UUID job ID

Job Data Service owns:
    - AI/ML-facing job record
    - Integer job ID used by AIML

Milestone 3 integration:
    Gateway Job UUID <-> Job Data Job Integer mapping is stored in
    Job.job_data_id.

Flow for job creation:

    Frontend
        |
        v
    Gateway :8000
        |
        +--> Gateway PostgreSQL
        |
        +--> Job Data :8004
                 |
                 v
             Job Data Job ID
        |
        v
    Gateway stores job_data_id
"""

import math
import re
import uuid

from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Optional, List

import requests

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    Body,
)

from sqlalchemy import (
    or_,
    cast,
    String,
)

from sqlalchemy.orm import (
    Session,
    joinedload,
)

from pydantic import ValidationError

from app.database import get_db
from app.models import (
    Job,
    Company,
    User,
    UserRole,
    JobType,
)

from app.schemas import (
    JobCreateRequest,
    JobUpdateRequest,
    JobOut,
    PaginatedJobsResponse,
)

from app.auth import (
    get_current_user,
    require_recruiter_or_admin,
)

from app.utils import serialize_job


# ==========================================================================
# Configuration
# ==========================================================================

import os

JOB_DATA_SERVICE_URL = os.getenv(
    "JOB_DATA_SERVICE_URL",
    "http://localhost:8004/api/v1",
).rstrip("/")

JOB_DATA_TIMEOUT_SECONDS = 15


# ==========================================================================
# Router
# ==========================================================================

router = APIRouter()


# ==========================================================================
# Job Data Service Helpers
# ==========================================================================

def _job_data_headers(user_id: uuid.UUID) -> dict:
    """
    Headers forwarded to Job Data Service.

    Job Data currently does not require Gateway JWT validation,
    but the user ID is forwarded for traceability.
    """
    return {
        "X-User-ID": str(user_id),
        "Content-Type": "application/json",
    }


def _job_data_request(
    method: str,
    path: str,
    user_id: uuid.UUID,
    *,
    json_data: Optional[dict] = None,
):
    """
    Make an HTTP request from Gateway to Job Data Service.

    No mock fallback is used.

    If Job Data is unavailable, the Gateway returns an explicit
    503 error instead of silently creating an isolated record.
    """

    url = f"{JOB_DATA_SERVICE_URL}{path}"

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_job_data_headers(user_id),
            json=json_data,
            timeout=JOB_DATA_TIMEOUT_SECONDS,
        )
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Job Data Service is unavailable. "
                f"Expected service at {JOB_DATA_SERVICE_URL}. "
                f"Error: {exc}"
            ),
        )

    if response.status_code >= 400:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text or "Job Data Service request failed."

        raise HTTPException(
            status_code=response.status_code,
            detail={
                "service": "job_data",
                "status_code": response.status_code,
                "response": detail,
            },
        )

    if not response.content:
        return None

    try:
        return response.json()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Job Data Service returned an invalid JSON response.",
        )


def _create_job_data_record(
    *,
    gateway_job: Job,
    gateway_company: Company,
    current_user: User,
) -> int:
    """
    Create the corresponding canonical AI/ML job in Job Data Service.

    IMPORTANT:
        Gateway Company.job_data_company_id must already contain the
        corresponding INTEGER company ID from Job Data Service.

    We never cast the Gateway UUID into an integer.
    """

    if gateway_company.job_data_company_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This Gateway company is not linked to a Job Data company. "
                "Create/link the corresponding Job Data company first, "
                "then create the job again."
            ),
        )

    job_payload = {
        "company_id": gateway_company.job_data_company_id,
        "title": gateway_job.title,
        "role_category": None,
        "description": gateway_job.description,
        "responsibilities": None,
        "requirements": None,
        "skills": gateway_job.skills_required or [],
        "required_skills": gateway_job.skills_required or [],
        "keywords": _extract_keywords(
            gateway_job.title,
            gateway_job.description,
        ),
        "job_type": _map_gateway_job_type_to_job_data(
            gateway_job.job_type
        ),
        "workplace_type": _infer_workplace_type(
            gateway_job.job_type,
            gateway_job.location,
        ),
        "location": gateway_job.location,
        "salary_min": (
            int(gateway_job.salary_min)
            if gateway_job.salary_min is not None
            else None
        ),
        "salary_max": (
            int(gateway_job.salary_max)
            if gateway_job.salary_max is not None
            else None
        ),
        "salary_currency": "INR",
        "salary_period": "Per Annum",
        "experience_level": _map_experience_level(
            gateway_job.experience_level
        ),
        "experience_years_min": _experience_years_min(
            gateway_job.experience_level
        ),
        "experience_years_max": _experience_years_max(
            gateway_job.experience_level
        ),
        "applicant_count": gateway_job.applicant_count or 0,
        "is_fresher_friendly": bool(
            gateway_job.fresher_friendly
        ),
        "is_active": bool(gateway_job.is_active),
    }

    response = _job_data_request(
        "POST",
        "/jobs",
        current_user.id,
        json_data=job_payload,
    )

    if not isinstance(response, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Job Data Service returned an invalid job response.",
        )

    job_data_id = response.get("job_id")

    if job_data_id is None:
        job_data_id = response.get("id")

    if job_data_id is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Job Data Service created a response without "
                "a job ID."
            ),
        )

    try:
        return int(job_data_id)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Job Data Service returned an invalid job ID."
            ),
        )


def _get_job_data_job(
    job_data_id: int,
    current_user: User,
) -> dict:
    """
    Retrieve the canonical Job Data record.
    """

    response = _job_data_request(
        "GET",
        f"/jobs/{job_data_id}",
        current_user.id,
    )

    if not isinstance(response, dict):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Invalid response from Job Data Service.",
        )

    return response


# ==========================================================================
# Job Data Mapping Helpers
# ==========================================================================

def _map_gateway_job_type_to_job_data(
    value: JobType,
) -> str:
    """
    Gateway JobType values:
        full_time
        part_time
        contract
        internship
        remote

    Job Data values:
        Full-time
        Part-time
        Contract
        Internship

    Job Data does not have a separate REMOTE job type.
    Remote is represented through workplace_type.
    """

    mapping = {
        JobType.FULL_TIME: "Full-time",
        JobType.PART_TIME: "Part-time",
        JobType.CONTRACT: "Contract",
        JobType.INTERNSHIP: "Internship",
        JobType.REMOTE: "Full-time",
    }

    return mapping.get(
        value,
        "Full-time",
    )


def _infer_workplace_type(
    job_type: JobType,
    location: str,
) -> str:
    """
    Infer Job Data workplace type from Gateway data.

    Gateway currently stores remote as a JobType, while Job Data
    has a separate workplace_type field.
    """

    if job_type == JobType.REMOTE:
        return "Remote"

    location_text = (location or "").strip().lower()

    if "hybrid" in location_text:
        return "Hybrid"

    if "remote" in location_text:
        return "Remote"

    return "On-site"


def _map_experience_level(
    value: Optional[str],
) -> str:
    """
    Convert Gateway experience labels into Job Data labels.
    """

    if not value:
        return "Fresher"

    normalized = str(value).strip().lower()

    if "fresher" in normalized:
        return "Fresher"

    if (
        "entry" in normalized
        or "junior" in normalized
        or "0-1" in normalized
        or "0 to 1" in normalized
    ):
        return "Entry-level"

    if "mid" in normalized:
        return "Mid-level"

    if "senior" in normalized:
        return "Senior"

    if "lead" in normalized:
        return "Lead"

    return "Entry-level"


def _experience_years_min(
    value: Optional[str],
) -> int:
    """
    Best-effort conversion of Gateway experience level
    into Job Data's numeric experience fields.
    """

    if not value:
        return 0

    normalized = str(value).strip().lower()

    if "fresher" in normalized:
        return 0

    if "entry" in normalized or "junior" in normalized:
        return 0

    if "mid" in normalized:
        return 2

    if "senior" in normalized:
        return 5

    if "lead" in normalized:
        return 7

    numbers = re.findall(r"\d+", normalized)

    if numbers:
        return int(numbers[0])

    return 0


def _experience_years_max(
    value: Optional[str],
) -> int:
    """
    Best-effort maximum experience mapping.
    """

    if not value:
        return 2

    normalized = str(value).strip().lower()

    if "fresher" in normalized:
        return 1

    if "entry" in normalized or "junior" in normalized:
        return 2

    if "mid" in normalized:
        return 5

    if "senior" in normalized:
        return 10

    if "lead" in normalized:
        return 20

    numbers = re.findall(r"\d+", normalized)

    if len(numbers) >= 2:
        return int(numbers[1])

    if len(numbers) == 1:
        return int(numbers[0])

    return 2


def _extract_keywords(
    title: str,
    description: str,
) -> List[str]:
    """
    Extract simple searchable keywords from the title and description.

    This is not an AI fallback. It only populates Job Data's keyword
    field so the AIML service has structured job metadata available.
    """

    text = f"{title or ''} {description or ''}".lower()

    stop_words = {
        "the",
        "and",
        "for",
        "with",
        "that",
        "this",
        "from",
        "are",
        "you",
        "your",
        "our",
        "will",
        "have",
        "has",
        "into",
        "about",
        "using",
        "use",
        "job",
        "role",
        "work",
        "years",
        "year",
        "required",
        "requirements",
        "responsibilities",
    }

    words = re.findall(
        r"[a-zA-Z][a-zA-Z0-9+#.\-]{2,}",
        text,
    )

    keywords = []

    for word in words:
        normalized = word.strip(".,-").lower()

        if normalized in stop_words:
            continue

        if normalized not in keywords:
            keywords.append(normalized)

    return keywords[:50]


# ==========================================================================
# Salary Helper
# ==========================================================================

def parse_salary_range(
    salary_range: Optional[str],
) -> tuple[Optional[Decimal], Optional[Decimal]]:
    """
    Convert frontend salary_range into salary_min/salary_max.

    Supported examples:

        "$80,000 - $120,000"
        "80000 - 120000"
        "₹8,00,000 - ₹12,00,000"
        "80000-120000"
    """

    if not salary_range:
        return None, None

    numbers = re.findall(
        r"\d+(?:,\d{2,3})*(?:\.\d+)?",
        salary_range,
    )

    if not numbers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Invalid salary_range. "
                "Example: '$80,000 - $120,000'"
            ),
        )

    try:
        parsed_numbers = [
            Decimal(number.replace(",", ""))
            for number in numbers
        ]
    except InvalidOperation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid salary_range value.",
        )

    if len(parsed_numbers) == 1:
        return parsed_numbers[0], None

    return parsed_numbers[0], parsed_numbers[1]


# ==========================================================================
# Frontend Payload Normalization
# ==========================================================================

def normalize_job_type(
    value,
) -> JobType:
    """
    Convert common frontend job-type values into Gateway JobType.
    """

    if isinstance(value, JobType):
        return value

    if value is None:
        return JobType.FULL_TIME

    normalized = str(value).strip().lower()

    aliases = {
        "full-time": JobType.FULL_TIME,
        "full time": JobType.FULL_TIME,
        "full_time": JobType.FULL_TIME,

        "part-time": JobType.PART_TIME,
        "part time": JobType.PART_TIME,
        "part_time": JobType.PART_TIME,

        "contract": JobType.CONTRACT,

        "internship": JobType.INTERNSHIP,
        "intern": JobType.INTERNSHIP,

        "remote": JobType.REMOTE,
    }

    if normalized in aliases:
        return aliases[normalized]

    try:
        return JobType(normalized)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Invalid job_type '{value}'. "
                "Allowed values: full_time, part_time, "
                "contract, internship, remote."
            ),
        )


def build_job_create_payload(
    payload: dict,
) -> JobCreateRequest:
    """
    Convert frontend fields into JobCreateRequest.
    """

    data = dict(payload)

    # ------------------------------------------------------------------
    # skills -> skills_required
    # ------------------------------------------------------------------

    if not data.get("skills_required") and data.get("skills"):
        skills = data.get("skills")

        if isinstance(skills, str):
            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

        if not isinstance(skills, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="skills must be a list of strings.",
            )

        data["skills_required"] = skills

    if "skills_required" not in data:
        data["skills_required"] = []

    # ------------------------------------------------------------------
    # salary_range -> salary_min / salary_max
    # ------------------------------------------------------------------

    salary_range = data.get("salary_range")

    if salary_range and (
        data.get("salary_min") is None
        and data.get("salary_max") is None
    ):
        salary_min, salary_max = parse_salary_range(
            salary_range
        )

        data["salary_min"] = salary_min
        data["salary_max"] = salary_max

    # ------------------------------------------------------------------
    # job_type normalization
    # ------------------------------------------------------------------

    if "job_type" in data:
        data["job_type"] = normalize_job_type(
            data["job_type"]
        )

    # ------------------------------------------------------------------
    # Validate using existing project schema
    # ------------------------------------------------------------------

    try:
        return JobCreateRequest.model_validate(data)

    except ValidationError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=exc.errors(),
        )


# ==========================================================================
# GET /jobs
# ==========================================================================

@router.get(
    "",
    response_model=PaginatedJobsResponse,
    summary="List / search jobs with pagination and filters",
)
def list_jobs(
    page: int = Query(
        1,
        ge=1,
        description="Page number, starting at 1",
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of results per page",
    ),
    keyword: Optional[str] = Query(
        None,
        description="Free-text search across title and description",
    ),
    location: Optional[str] = Query(
        None,
        description="Filter by location",
    ),
    job_type: Optional[JobType] = Query(
        None,
        description="Filter by job type",
    ),
    company_id: Optional[uuid.UUID] = Query(
        None,
        description="Filter by company",
    ),
    skill: Optional[List[str]] = Query(
        None,
        description="Filter by required skills",
    ),
    salary_min: Optional[Decimal] = Query(
        None,
        ge=0,
        description="Minimum salary",
    ),
    salary_max: Optional[Decimal] = Query(
        None,
        ge=0,
        description="Maximum salary",
    ),
    sort_by: str = Query(
        "posted_at",
        pattern="^(posted_at|salary_min|salary_max|applicant_count)$",
    ),
    sort_order: str = Query(
        "desc",
        pattern="^(asc|desc)$",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.is_active == 1)
    )

    if keyword:
        like_pattern = f"%{keyword.strip()}%"

        query = query.filter(
            or_(
                Job.title.ilike(like_pattern),
                Job.description.ilike(like_pattern),
            )
        )

    if location:
        query = query.filter(
            Job.location.ilike(
                f"%{location.strip()}%"
            )
        )

    if job_type:
        query = query.filter(
            Job.job_type == job_type
        )

    if company_id:
        query = query.filter(
            Job.company_id == company_id
        )

    if skill:
        skill_filters = [
            cast(
                Job.skills_required,
                String,
            ).ilike(f"%{s}%")
            for s in skill
        ]

        query = query.filter(
            or_(*skill_filters)
        )

    if salary_min is not None:
        query = query.filter(
            or_(
                Job.salary_max.is_(None),
                Job.salary_max >= salary_min,
            )
        )

    if salary_max is not None:
        query = query.filter(
            or_(
                Job.salary_min.is_(None),
                Job.salary_min <= salary_max,
            )
        )

    total = query.count()

    sort_column = getattr(
        Job,
        sort_by,
    )

    if sort_order == "desc":
        sort_column = sort_column.desc()
    else:
        sort_column = sort_column.asc()

    jobs = (
        query
        .order_by(sort_column)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    total_pages = (
        math.ceil(total / page_size)
        if total > 0
        else 0
    )

    return PaginatedJobsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        results=[
            serialize_job(job)
            for job in jobs
        ],
    )


# ==========================================================================
# GET /jobs/search
# ==========================================================================

@router.get(
    "/search",
    response_model=PaginatedJobsResponse,
    summary="Search jobs with advanced filters",
)
def search_jobs(
    page: int = Query(
        1,
        ge=1,
    ),
    page_size: int = Query(
        20,
        ge=1,
        le=100,
    ),
    keyword: Optional[str] = Query(
        None,
        description="Search title, description, or company name",
    ),
    location: Optional[str] = Query(
        None,
        description="Filter by location",
    ),
    salary_min: Optional[Decimal] = Query(
        None,
        ge=0,
    ),
    salary_max: Optional[Decimal] = Query(
        None,
        ge=0,
    ),
    job_type: Optional[JobType] = Query(
        None,
    ),
    experience_level: Optional[str] = Query(
        None,
    ),
    fresher_friendly: Optional[bool] = Query(
        None,
    ),
    low_competition: Optional[bool] = Query(
        None,
    ),
    recently_posted: Optional[bool] = Query(
        None,
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if (
        salary_min is not None
        and salary_max is not None
        and salary_min > salary_max
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="salary_min cannot exceed salary_max",
        )

    query = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.is_active == 1)
    )

    if keyword:
        like_pattern = f"%{keyword.strip()}%"

        query = (
            query
            .join(Company)
            .filter(
                or_(
                    Job.title.ilike(like_pattern),
                    Job.description.ilike(like_pattern),
                    Company.name.ilike(like_pattern),
                )
            )
        )

    if location:
        query = query.filter(
            Job.location.ilike(
                f"%{location.strip()}%"
            )
        )

    if salary_min is not None:
        query = query.filter(
            or_(
                Job.salary_max.is_(None),
                Job.salary_max >= salary_min,
            )
        )

    if salary_max is not None:
        query = query.filter(
            or_(
                Job.salary_min.is_(None),
                Job.salary_min <= salary_max,
            )
        )

    if job_type is not None:
        query = query.filter(
            Job.job_type == job_type
        )

    if experience_level:
        query = query.filter(
            Job.experience_level.ilike(
                experience_level.strip()
            )
        )

    if fresher_friendly is not None:
        query = query.filter(
            Job.fresher_friendly == fresher_friendly
        )

    if low_competition is not None:
        query = query.filter(
            Job.low_competition == low_competition
        )

    if recently_posted:
        cutoff = (
            datetime.now(timezone.utc)
            - timedelta(days=30)
        )

        query = query.filter(
            Job.created_at >= cutoff
        )

    total = query.count()

    jobs = (
        query
        .order_by(Job.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return PaginatedJobsResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(
            math.ceil(total / page_size)
            if total
            else 0
        ),
        results=[
            serialize_job(job)
            for job in jobs
        ],
    )


# ==========================================================================
# GET /jobs/{job_id}
# ==========================================================================

@router.get(
    "/{job_id}",
    response_model=JobOut,
    summary="Get a single job",
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
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    return serialize_job(job)


# ==========================================================================
# POST /jobs
# ==========================================================================

@router.post(
    "",
    response_model=JobOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new integrated job posting",
    dependencies=[
        Depends(require_recruiter_or_admin)
    ],
)
def create_job(
    payload: dict = Body(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create one logical job across Gateway and Job Data.

    Order:

        1. Validate frontend payload.
        2. Validate Gateway company.
        3. Validate recruiter ownership.
        4. Create Gateway Job.
        5. Create Job Data Job.
        6. Save Job Data integer ID into Gateway Job.job_data_id.

    No mock record is created if Job Data is unavailable.
    """

    # ------------------------------------------------------------------
    # 1. Normalize and validate request
    # ------------------------------------------------------------------

    validated_payload = build_job_create_payload(
        payload
    )

    # ------------------------------------------------------------------
    # 2. Find Gateway company
    # ------------------------------------------------------------------

    company = (
        db.query(Company)
        .filter(
            Company.id == validated_payload.company_id
        )
        .first()
    )

    if company is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found",
        )

    # ------------------------------------------------------------------
    # 3. Recruiter ownership
    # ------------------------------------------------------------------

    if (
        current_user.role == UserRole.RECRUITER
        and current_user.company_id != company.id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Recruiters may only create jobs "
                "for their own company"
            ),
        )

    # ------------------------------------------------------------------
    # 4. Create Gateway job
    # ------------------------------------------------------------------

    job = Job(
        company_id=validated_payload.company_id,
        posted_by=current_user.id,
        title=validated_payload.title,
        description=validated_payload.description,
        location=validated_payload.location,
        job_type=validated_payload.job_type,
        experience_level=validated_payload.experience_level,
        salary_min=validated_payload.salary_min,
        salary_max=validated_payload.salary_max,
        skills_required=(
            validated_payload.skills_required or []
        ),
        fresher_friendly=(
            validated_payload.fresher_friendly
        ),
        low_competition=(
            validated_payload.low_competition
        ),
        applicant_count=0,
        is_active=1,
        job_data_id=None,
    )

    db.add(job)

    try:
        db.flush()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Gateway job.",
        )

    # ------------------------------------------------------------------
    # 5. Create corresponding Job Data record
    # ------------------------------------------------------------------

    try:
        job_data_id = _create_job_data_record(
            gateway_job=job,
            gateway_company=company,
            current_user=current_user,
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception as exc:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "Failed to create corresponding Job Data record. "
                f"Error: {exc}"
            ),
        )

    # ------------------------------------------------------------------
    # 6. Store Job Data mapping
    # ------------------------------------------------------------------

    job.job_data_id = job_data_id

    try:
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=(
                "Gateway job was created but its Job Data mapping "
                "could not be saved."
            ),
        )

    db.refresh(job)

    # ------------------------------------------------------------------
    # 7. Reload company relationship
    # ------------------------------------------------------------------

    job = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.id == job.id)
        .first()
    )

    return serialize_job(job)


# ==========================================================================
# PATCH /jobs/{job_id}
# ==========================================================================

@router.patch(
    "/{job_id}",
    response_model=JobOut,
    summary="Update an existing job posting",
    dependencies=[
        Depends(require_recruiter_or_admin)
    ],
)
def update_job(
    job_id: uuid.UUID,
    payload: JobUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Update the Gateway job.

    Job Data currently exposes GET/POST job APIs but does not expose
    a PATCH /jobs/{id} endpoint in the provided Job Data service.

    Therefore Gateway remains the write owner for job edits for now.
    The existing Job Data mapping is preserved.
    """

    job = (
        db.query(Job)
        .options(joinedload(Job.company))
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # ------------------------------------------------------------------
    # Recruiter ownership
    # ------------------------------------------------------------------

    if (
        current_user.role == UserRole.RECRUITER
        and current_user.company_id != job.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Recruiters may only update jobs "
                "belonging to their own company"
            ),
        )

    # ------------------------------------------------------------------
    # Apply update
    # ------------------------------------------------------------------

    update_data = payload.model_dump(
        exclude_unset=True
    )

    if "is_active" in update_data:
        update_data["is_active"] = (
            1
            if update_data["is_active"]
            else 0
        )

    if "job_type" in update_data:
        update_data["job_type"] = normalize_job_type(
            update_data["job_type"]
        )

    for field, value in update_data.items():
        setattr(
            job,
            field,
            value,
        )

    try:
        db.commit()

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update job posting.",
        )

    db.refresh(job)

    return serialize_job(job)


# ==========================================================================
# DELETE /jobs/{job_id}
# ==========================================================================

@router.delete(
    "/{job_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a job posting",
    dependencies=[
        Depends(require_recruiter_or_admin)
    ],
)
def delete_job(
    job_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete the Gateway job.

    Job Data currently does not expose DELETE /jobs/{id}, so the
    Job Data record is intentionally not fabricated or incorrectly
    addressed here.

    Once Job Data exposes a DELETE endpoint, this controller can
    propagate deletion using job.job_data_id.
    """

    job = (
        db.query(Job)
        .filter(Job.id == job_id)
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    # ------------------------------------------------------------------
    # Recruiter ownership
    # ------------------------------------------------------------------

    if (
        current_user.role == UserRole.RECRUITER
        and current_user.company_id != job.company_id
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(
                "Recruiters may only delete jobs "
                "belonging to their own company"
            ),
        )

    db.delete(job)
    db.commit()

    return None