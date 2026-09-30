
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models import Job, User
from app.schemas import RecommendationItem, RecommendationResponse


router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"],
)


# ---------------------------------------------------------------------------
# Internal service URLs
# ---------------------------------------------------------------------------

AIML_SERVICE_URL = getattr(
    settings,
    "AIML_SERVICE_URL",
    "http://localhost:8002/api/v1",
).rstrip("/")

JOB_DATA_SERVICE_URL = getattr(
    settings,
    "JOB_DATA_SERVICE_URL",
    "http://localhost:8004/api/v1",
).rstrip("/")

REQUEST_TIMEOUT = 20


# ---------------------------------------------------------------------------
# Internal service helpers
# ---------------------------------------------------------------------------

def _get_headers(user_id: str) -> dict[str, str]:
    """
    Headers sent to internal SwipeX services.
    """

    return {
        "X-User-ID": str(user_id),
    }


def _call_service(
    method: str,
    url: str,
    *,
    user_id: str,
    params: dict[str, Any] | None = None,
) -> Any:
    """
    Call an internal SwipeX service.

    There is intentionally NO mock-data or local fallback.
    If AIML or Job Data is unavailable, the Gateway returns
    an explicit service error.
    """

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=_get_headers(user_id),
            params=params,
            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                f"Required SwipeX service is unavailable: "
                f"{url}. Error: {exc}"
            ),
        ) from exc

    if response.status_code >= 400:
        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise HTTPException(
            status_code=response.status_code,
            detail=detail,
        )

    try:
        return response.json()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                f"Invalid JSON response received from "
                f"SwipeX service: {url}"
            ),
        ) from exc


# ---------------------------------------------------------------------------
# Job Data → Gateway ID mapping
# ---------------------------------------------------------------------------

def _get_gateway_job_by_job_data_id(
    db: Session,
    job_data_id: int,
) -> Job | None:
    """
    Resolve a canonical Job Data integer ID to the corresponding
    Gateway UUID job.

    Mapping:

        Job Data:
            jobs.id = integer

        Gateway:
            jobs.job_data_id = Job Data integer
            jobs.id = Gateway UUID

    The Gateway UUID is what the frontend must receive.
    """

    return (
        db.query(Job)
        .filter(
            Job.job_data_id == int(job_data_id),
            Job.is_active.is_(True),
        )
        .first()
    )


# ---------------------------------------------------------------------------
# Job Data details
# ---------------------------------------------------------------------------

def _get_job_details(
    job_data_id: int,
    user_id: str,
) -> dict[str, Any] | None:
    """
    Retrieve canonical job details from the Job Data Service.

    `job_data_id` is always the integer ID owned by Job Data.
    """

    try:
        response = requests.get(
            f"{JOB_DATA_SERVICE_URL}/jobs/{int(job_data_id)}",
            headers=_get_headers(user_id),
            timeout=REQUEST_TIMEOUT,
        )

    except requests.RequestException:
        return None

    if response.status_code == 404:
        return None

    if response.status_code >= 400:
        return None

    try:
        data = response.json()

    except ValueError:
        return None

    return data if isinstance(data, dict) else None


# ---------------------------------------------------------------------------
# Job normalization
# ---------------------------------------------------------------------------

def _normalize_job(
    job: dict[str, Any],
    gateway_job: Job | None = None,
) -> dict[str, Any]:
    """
    Convert Job Data's representation into the Gateway/frontend
    job representation.

    IMPORTANT:
    The returned `id` and `job_id` are Gateway UUIDs whenever
    the corresponding Gateway job exists.

    This prevents the frontend from receiving the Job Data integer
    as if it were a Gateway UUID.
    """

    company = job.get("company")

    if isinstance(company, dict):
        company_name = (
            company.get("name")
            or company.get("company_name")
            or ""
        )

        company_id = company.get("id")

    else:
        company_name = str(company or "")
        company_id = job.get("company_id")

    skills = (
        job.get("skills")
        or job.get("required_skills")
        or []
    )

    if isinstance(skills, str):
        skills = [
            item.strip()
            for item in skills.split(",")
            if item.strip()
        ]

    # ---------------------------------------------------------------
    # Gateway UUID is the public ID.
    # Job Data integer is used only internally for service-to-service
    # communication.
    # ---------------------------------------------------------------

    if gateway_job is not None:
        public_job_id = str(gateway_job.id)

        gateway_company_id = gateway_job.company_id

        if gateway_job.company is not None:
            gateway_company_name = gateway_job.company.name
        else:
            gateway_company_name = company_name

        if gateway_company_id is not None:
            company_id = gateway_company_id

        if gateway_company_name:
            company_name = gateway_company_name

    else:
        public_job_id = job.get(
            "job_id",
            job.get("id"),
        )

    return {
        "id": public_job_id,
        "job_id": public_job_id,

        "company_id": company_id,
        "company_name": company_name,

        "title": job.get(
            "title",
            "",
        ),

        "description": job.get(
            "description",
            "",
        ),

        "location": job.get(
            "location",
            "",
        ),

        "job_type": (
            job.get("type")
            or job.get("job_type")
            or "Full-time"
        ),

        "workplace_type": job.get(
            "workplace_type",
            "",
        ),

        "experience_level": job.get(
            "experience_level",
            "",
        ),

        "salary_min": job.get(
            "salary_min"
        ),

        "salary_max": job.get(
            "salary_max"
        ),

        "salary_range": job.get(
            "salary_range",
            "Competitive",
        ),

        "skills_required": skills,
        "skills": skills,

        "fresher_friendly": bool(
            job.get(
                "is_fresher_friendly",
                job.get(
                    "fresher_friendly",
                    True,
                ),
            )
        ),

        "low_competition": (
            str(
                job.get(
                    "competition_level",
                    "",
                )
            ).lower()
            == "low"
        ),

        "applicant_count": job.get(
            "applicant_count",
            0,
        ),

        "is_active": bool(
            job.get(
                "is_active",
                True,
            )
        ),

        "posted_at": job.get(
            "posted_at"
        ),

        "created_at": job.get(
            "created_at",
            job.get("posted_at"),
        ),

        "competition_level": job.get(
            "competition_level",
            "Medium",
        ),

        "posted_time": job.get(
            "posted_time",
            "",
        ),
    }


# ---------------------------------------------------------------------------
# Recommendation item construction
# ---------------------------------------------------------------------------

def _build_recommendation_item(
    recommendation: dict[str, Any],
    job: dict[str, Any],
    gateway_job: Job | None = None,
) -> RecommendationItem:
    """
    Combine AIML scoring data with canonical Job Data details.

    AIML owns recommendation scoring.
    Job Data owns job information.
    Gateway owns the public UUID mapping.
    """

    match_score = float(
        recommendation.get(
            "match_percentage",
            recommendation.get(
                "match_score",
                0.0,
            ),
        )
    )

    reason_tags = recommendation.get(
        "reason_tags",
        recommendation.get(
            "recommendation_tags",
            [],
        ),
    )

    if not isinstance(reason_tags, list):
        reason_tags = []

    semantic_score = recommendation.get(
        "semantic_match_score"
    )

    return RecommendationItem(
        job=_normalize_job(
            job,
            gateway_job=gateway_job,
        ),

        match_score=match_score,

        match_reasons=reason_tags,

        semantic_match_score=(
            float(semantic_score)
            if semantic_score is not None
            else None
        ),

        recommendation_tags=reason_tags,
    )


# ---------------------------------------------------------------------------
# GET /api/v1/recommendations
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=RecommendationResponse,
    summary="Get AI-powered personalized job recommendations",
)
def get_recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=100,
    ),

    workplace_type: str | None = Query(
        None,
    ),

    hybrid: bool = Query(
        False,
    ),

    current_user: User = Depends(
        get_current_user
    ),

    db: Session = Depends(
        get_db
    ),
):
    """
    Generate personalized recommendations for the authenticated user.

    Integration flow:

        Frontend
            ↓
        Gateway
            ↓
        AIML
            ↓
        Job Data
            ↓
        AIML recommendation scores
            ↓
        Gateway resolves Job Data ID → Gateway UUID
            ↓
        Frontend-compatible response

    Source of truth:

        Gateway:
            authentication + public job UUID

        Job Data:
            canonical job information

        AIML:
            recommendation scoring
    """

    user_id = str(current_user.id)

    # ------------------------------------------------------------------
    # STEP 1
    # Ask AIML for personalized recommendation scores.
    # ------------------------------------------------------------------

    params: dict[str, Any] = {
        "user_id": user_id,
        "limit": limit,
        "hybrid": hybrid,
    }

    if workplace_type:
        params["workplace_type"] = workplace_type

    recommendations = _call_service(
        "GET",
        f"{AIML_SERVICE_URL}/recommendations",
        user_id=user_id,
        params=params,
    )

    if not isinstance(
        recommendations,
        list,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML recommendation service returned "
                "an unexpected response."
            ),
        )

    # ------------------------------------------------------------------
    # STEP 2
    # Enrich every recommendation with canonical Job Data details.
    # ------------------------------------------------------------------

    result_items: list[RecommendationItem] = []

    for recommendation in recommendations:

        if not isinstance(
            recommendation,
            dict,
        ):
            continue

        job_data_id = recommendation.get(
            "job_id"
        )

        if job_data_id is None:
            continue

        # --------------------------------------------------------------
        # Validate that AIML returned a numeric Job Data ID.
        # --------------------------------------------------------------

        try:
            numeric_job_data_id = int(
                job_data_id
            )

        except (
            TypeError,
            ValueError,
        ):
            # AIML must return Job Data IDs.
            # Never silently reinterpret a UUID as a Job Data ID.
            continue

        # --------------------------------------------------------------
        # Resolve Job Data integer → Gateway UUID.
        # --------------------------------------------------------------

        gateway_job = (
            _get_gateway_job_by_job_data_id(
                db,
                numeric_job_data_id,
            )
        )

        if gateway_job is None:
            # This means the Gateway does not have a synchronized
            # record for the recommended Job Data job.
            #
            # Do NOT expose the Job Data integer as the public
            # Gateway job ID.
            continue

        # --------------------------------------------------------------
        # Retrieve canonical job details from Job Data.
        # --------------------------------------------------------------

        job = _get_job_details(
            numeric_job_data_id,
            user_id,
        )

        if not job:
            # Do not fabricate job details.
            continue

        # --------------------------------------------------------------
        # Build frontend-compatible recommendation.
        # --------------------------------------------------------------

        try:
            result_items.append(
                _build_recommendation_item(
                    recommendation,
                    job,
                    gateway_job=gateway_job,
                )
            )

        except Exception:
            # One malformed recommendation should not break
            # all other valid recommendations.
            continue

    # ------------------------------------------------------------------
    # STEP 3
    # Return the Gateway response.
    # ------------------------------------------------------------------

    return RecommendationResponse(
        user_id=current_user.id,

        generated_at=datetime.now(
            timezone.utc
        ),

        engine="aiml",

        count=len(
            result_items
        ),

        recommendations=result_items,
    )
