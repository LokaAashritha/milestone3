
"""
app/controllers/ats_controller.py

SwipeX Milestone 3 - Real ATS Scoring & AI Suggestions Integration.

Architecture:

    Frontend
        |
        | POST /api/v1/ats/score
        | POST /api/v1/ats/suggestions
        v
    Backend Gateway :8000
        |
        | authenticate user
        | verify resume ownership
        | verify Gateway job
        | resolve Gateway UUID -> Job Data integer ID
        v
    AIML Service :8002
        |
        v
    Job Data Service :8004
        |
        v
    Real ATS / AI result

Responsibilities:

Gateway:
    - Authentication
    - Resume ownership verification
    - Gateway job verification
    - Gateway Job UUID -> Job Data job ID mapping
    - AIML orchestration
    - Response normalization

AIML:
    - ATS calculation
    - Semantic similarity
    - Skill matching
    - Keyword matching
    - Missing-skill detection
    - AI suggestions

Job Data:
    - Canonical job data
    - Canonical resume data

No mock ATS score or silent fallback is used.
"""

from __future__ import annotations

import uuid
from typing import Any, List, Optional

import requests

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)

from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.core.config import settings
from app.database import get_db
from app.models import Job, Resume, User


# ==========================================================================
# Router
# ==========================================================================

router = APIRouter(
    prefix="/ats",
    tags=["ATS"],
)


# ==========================================================================
# Configuration
# ==========================================================================

AIML_URL = getattr(
    settings,
    "AIML_SERVICE_URL",
    "http://localhost:8002/api/v1",
).rstrip("/")

AIML_TIMEOUT_SECONDS = 30


# ==========================================================================
# Request / Response Schemas
# ==========================================================================

class ATSScoreRequest(BaseModel):
    """
    Frontend/Gateway request.

    The frontend uses Gateway UUIDs.

    The Gateway converts the Gateway job UUID into the canonical
    Job Data integer ID before contacting AIML.
    """

    resume_id: uuid.UUID
    job_id: uuid.UUID


class ATSScoreResponse(BaseModel):
    overall_score: float
    skill_score: float
    keyword_score: float
    semantic_match_score: float

    missing_skills: List[str] = Field(
        default_factory=list
    )

    missing_keywords: List[str] = Field(
        default_factory=list
    )


class AISuggestionItem(BaseModel):
    title: str
    detail: str
    category: Optional[str] = "general"


class AISuggestionsResponse(BaseModel):
    resume_id: uuid.UUID
    job_id: uuid.UUID
    overall_feedback: str
    suggestions: List[AISuggestionItem]


# ==========================================================================
# Gateway Database Helpers
# ==========================================================================

def get_user_resume(
    db: Session,
    resume_id: uuid.UUID,
    current_user: User,
) -> Resume:
    """
    Retrieve a resume belonging to the authenticated user.
    """

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id,
        )
        .first()
    )

    if resume is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found.",
        )

    return resume


def get_user_job(
    db: Session,
    job_id: uuid.UUID,
) -> Job:
    """
    Retrieve the active Gateway job.

    The Gateway UUID is the public job identifier.
    """

    job = (
        db.query(Job)
        .filter(
            Job.id == job_id,
            Job.is_active.is_(True),
        )
        .first()
    )

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found.",
        )

    return job


# ==========================================================================
# Job ID Mapping
# ==========================================================================

def get_job_data_id(
    job: Job,
) -> int:
    """
    Resolve the Gateway Job UUID to the canonical Job Data integer ID.

    Mapping:

        Gateway:
            Job.id           -> UUID
            Job.job_data_id  -> Job Data integer ID

        Job Data:
            jobs.id          -> integer

    The Gateway UUID must NEVER be sent to AIML as the Job Data ID.
    """

    job_data_id = getattr(
        job,
        "job_data_id",
        None,
    )

    if job_data_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "This Gateway job is not synchronized with "
                "the Job Data Service. "
                "The job_data_id mapping is missing."
            ),
        )

    try:
        return int(job_data_id)

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "The Gateway job contains an invalid "
                "Job Data ID mapping."
            ),
        ) from exc


# ==========================================================================
# AIML Service Helper
# ==========================================================================

def call_aiml_get(
    endpoint: str,
    *,
    user_id: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """
    Call an AIML GET endpoint.

    No mock or fallback response is generated.
    """

    url = (
        f"{AIML_URL}/"
        f"{endpoint.lstrip('/')}"
    )

    try:
        response = requests.get(
            url,
            headers={
                "X-User-ID": str(user_id),
            },
            params=params,
            timeout=AIML_TIMEOUT_SECONDS,
        )

    except requests.exceptions.Timeout as exc:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                "AIML service request timed out. "
                "Please make sure the AIML service is "
                "running on port 8002."
            ),
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Unable to connect to the AIML service. "
                "Please make sure the AIML service is "
                "running on port 8002."
            ),
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML service request failed: "
                f"{str(exc)}"
            ),
        ) from exc

    # ------------------------------------------------------------------
    # AIML returned an error
    # ------------------------------------------------------------------

    if (
        response.status_code < 200
        or response.status_code >= 300
    ):
        try:
            aiml_error = response.json()

        except ValueError:
            aiml_error = response.text

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "message": (
                    "AIML service returned an error."
                ),
                "aiml_status_code": (
                    response.status_code
                ),
                "aiml_response": aiml_error,
            },
        )

    # ------------------------------------------------------------------
    # Validate JSON
    # ------------------------------------------------------------------

    try:
        result = response.json()

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML service returned invalid JSON."
            ),
        ) from exc

    if not isinstance(
        result,
        dict,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML service returned an unexpected "
                "response format."
            ),
        )

    return result


# ==========================================================================
# Response Normalization Helpers
# ==========================================================================

def _get_numeric_score(
    data: dict[str, Any],
    *keys: str,
) -> float | None:
    """
    Read the first available numeric score from an AIML response.

    Returns None when the value is genuinely unavailable.
    """

    for key in keys:

        value = data.get(key)

        if value is None:
            continue

        try:
            return float(value)

        except (
            TypeError,
            ValueError,
        ):
            continue

    return None


def _normalize_string_list(
    value: Any,
) -> list[str]:
    """
    Normalize an AIML list-like response field.
    """

    if value is None:
        return []

    if isinstance(
        value,
        list,
    ):
        return [
            str(item)
            for item in value
            if item is not None
        ]

    if isinstance(
        value,
        str,
    ):
        if not value.strip():
            return []

        return [
            item.strip()
            for item in value.split(",")
            if item.strip()
        ]

    return [str(value)]


# ==========================================================================
# Endpoint 1 - ATS Score
# ==========================================================================

@router.post(
    "/score",
    response_model=ATSScoreResponse,
    status_code=status.HTTP_200_OK,
)
def calculate_ats_score(
    payload: ATSScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Calculate a real ATS score through AIML.

    Flow:

        Frontend
            |
            | Gateway resume UUID
            | Gateway job UUID
            v
        Gateway
            |
            | verify ownership
            | resolve job_data_id
            v
        AIML
            |
            | resume_id
            | Job Data job_id
            v
        Job Data
            |
            v
        Real ATS calculation
    """

    # ------------------------------------------------------------------
    # 1. Verify resume ownership
    # ------------------------------------------------------------------

    resume = get_user_resume(
        db=db,
        resume_id=payload.resume_id,
        current_user=current_user,
    )

    # ------------------------------------------------------------------
    # 2. Verify Gateway job
    # ------------------------------------------------------------------

    job = get_user_job(
        db=db,
        job_id=payload.job_id,
    )

    # ------------------------------------------------------------------
    # 3. Verify resume parsing
    # ------------------------------------------------------------------

    if resume.parsed_status != "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume has not been successfully "
                "parsed yet. Current parsing status: "
                f"{resume.parsed_status}"
            ),
        )

    # ------------------------------------------------------------------
    # 4. Resolve Gateway UUID -> Job Data integer
    # ------------------------------------------------------------------

    job_data_id = get_job_data_id(
        job
    )

    # ------------------------------------------------------------------
    # 5. Call AIML
    # ------------------------------------------------------------------
    #
    # IMPORTANT:
    #
    # The Gateway's `job.id` is a UUID.
    #
    # AIML's recommendation/ATS engine works with Job Data's
    # canonical integer job ID.
    #
    # Therefore we send `job_data_id`, not `job.id`.
    # ------------------------------------------------------------------

    aiml_result = call_aiml_get(
        f"/resume/{resume.id}/ats-score",
        user_id=str(
            current_user.id
        ),
        params={
            "job_id": job_data_id,
        },
    )

    # ------------------------------------------------------------------
    # 6. Read overall score
    # ------------------------------------------------------------------

    overall_score = _get_numeric_score(
        aiml_result,
        "match_score",
        "overall_score",
    )

    if overall_score is None:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML ATS response does not contain "
                "a valid 'match_score' or 'overall_score'."
            ),
        )

    # ------------------------------------------------------------------
    # 7. Read component scores
    # ------------------------------------------------------------------

    skill_score = _get_numeric_score(
        aiml_result,
        "skill_score",
    )

    keyword_score = _get_numeric_score(
        aiml_result,
        "keyword_score",
    )

    semantic_score = _get_numeric_score(
        aiml_result,
        "semantic_match_score",
        "semantic_score",
    )

    # ------------------------------------------------------------------
    # AIML should now return these component scores because the
    # integrated AIML ATS scorer exposes:
    #
    #   skill_score
    #   keyword_score
    #   semantic_match_score
    #
    # Do NOT replace missing component values with the overall score.
    # That would create an artificial/fake component score.
    # ------------------------------------------------------------------

    if skill_score is None:
        skill_score = 0.0

    if keyword_score is None:
        keyword_score = 0.0

    if semantic_score is None:
        semantic_score = 0.0

    # ------------------------------------------------------------------
    # 8. Missing skills / keywords
    # ------------------------------------------------------------------

    missing_skills = _normalize_string_list(
        aiml_result.get(
            "missing_skills"
        )
    )

    missing_keywords = _normalize_string_list(
        aiml_result.get(
            "missing_keywords"
        )
    )

    # ------------------------------------------------------------------
    # 9. Return normalized Gateway response
    # ------------------------------------------------------------------

    return ATSScoreResponse(
        overall_score=overall_score,
        skill_score=skill_score,
        keyword_score=keyword_score,
        semantic_match_score=semantic_score,
        missing_skills=missing_skills,
        missing_keywords=missing_keywords,
    )


# ==========================================================================
# Endpoint 2 - AI Suggestions
# ==========================================================================

@router.post(
    "/suggestions",
    response_model=AISuggestionsResponse,
    status_code=status.HTTP_200_OK,
)
def get_ats_suggestions(
    payload: ATSScoreRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    """
    Generate real AI/rule-based resume improvement suggestions
    through the AIML service.

    No suggestion is generated by the Gateway.
    """

    # ------------------------------------------------------------------
    # 1. Verify resume ownership
    # ------------------------------------------------------------------

    resume = get_user_resume(
        db=db,
        resume_id=payload.resume_id,
        current_user=current_user,
    )

    # ------------------------------------------------------------------
    # 2. Verify Gateway job
    # ------------------------------------------------------------------

    job = get_user_job(
        db=db,
        job_id=payload.job_id,
    )

    # ------------------------------------------------------------------
    # 3. Verify resume parsing
    # ------------------------------------------------------------------

    if resume.parsed_status != "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Resume has not been successfully "
                "parsed yet. Current parsing status: "
                f"{resume.parsed_status}"
            ),
        )

    # ------------------------------------------------------------------
    # 4. Resolve Gateway UUID -> Job Data integer
    # ------------------------------------------------------------------

    job_data_id = get_job_data_id(
        job
    )

    # ------------------------------------------------------------------
    # 5. Call AIML suggestions endpoint
    # ------------------------------------------------------------------

    result = call_aiml_get(
        f"/resume/{resume.id}/suggestions",
        user_id=str(
            current_user.id
        ),
        params={
            "job_id": job_data_id,
        },
    )

    # ------------------------------------------------------------------
    # 6. Normalize overall feedback
    # ------------------------------------------------------------------

    overall_feedback = result.get(
        "overall_feedback",
        result.get(
            "summary",
            "",
        ),
    )

    # ------------------------------------------------------------------
    # 7. Normalize suggestions
    # ------------------------------------------------------------------

    suggestions_data = result.get(
        "suggestions",
        [],
    )

    if not isinstance(
        suggestions_data,
        list,
    ):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "AIML suggestions response contains "
                "an invalid suggestions format."
            ),
        )

    normalized_suggestions: list[
        AISuggestionItem
    ] = []

    for item in suggestions_data:

        if not isinstance(
            item,
            dict,
        ):
            continue

        title = item.get(
            "title",
            item.get(
                "category",
                "General",
            ),
        )

        detail = item.get(
            "detail",
            item.get(
                "suggestion",
                "",
            ),
        )

        category = item.get(
            "category",
            "general",
        )

        normalized_suggestions.append(
            AISuggestionItem(
                title=str(title),
                detail=str(detail),
                category=str(category),
            )
        )

    # ------------------------------------------------------------------
    # 8. Return real AIML suggestions
    # ------------------------------------------------------------------

    return AISuggestionsResponse(
        resume_id=payload.resume_id,
        job_id=payload.job_id,
        overall_feedback=str(
            overall_feedback
        ),
        suggestions=normalized_suggestions,
    )