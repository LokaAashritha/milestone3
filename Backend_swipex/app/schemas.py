"""
app/schemas.py

Pydantic (v2) schemas used for request validation and response serialization
across the Auth, Job, Company, Swipe, Recommendation, Resume, and ATS services.

Milestone 3 integration:
- Preserves the existing backend API contracts.
- Adds UI-friendly Job and Company fields.
- Adds ATS scoring and suggestion response schemas.
- Uses Pydantic v2 syntax throughout.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    ConfigDict,
    field_validator,
)

from app.models import UserRole, JobType, SwipeAction


# ==========================================================================
# Shared / Generic
# ==========================================================================

class ErrorResponse(BaseModel):
    detail: str


# ==========================================================================
# Auth / User schemas
# ==========================================================================

class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = UserRole.JOB_SEEKER
    skills: List[str] = Field(default_factory=list)

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")

        return v


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    full_name: Optional[str] = None
    role: UserRole
    skills: List[str] = Field(default_factory=list)
    company_id: Optional[uuid.UUID] = None
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut


class JWTClaims(BaseModel):
    """Claims included in an access token."""

    id: uuid.UUID
    email: EmailStr
    role: UserRole
    skills: List[str] = Field(default_factory=list)


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ==========================================================================
# Company schemas
# ==========================================================================

class CompanyCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    about: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=150)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    about: Optional[str] = None
    industry: Optional[str] = Field(None, max_length=150)
    location: Optional[str] = Field(None, max_length=255)
    website: Optional[str] = Field(None, max_length=255)
    logo_url: Optional[str] = Field(None, max_length=500)


class CompanyOut(BaseModel):
    """
    Company response schema.

    Existing fields are preserved.

    Milestone 3 UI-compatible fields:
    - employee_count
    - openings

    These are optional/computed fields so existing database models
    do not immediately need matching columns.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    about: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    created_at: datetime
    job_count: int = 0

    # UI-compatible company fields
    employee_count: Optional[str] = "50-200"
    openings: Optional[int] = 0


# ==========================================================================
# Job schemas
# ==========================================================================

class JobCreateRequest(BaseModel):
    company_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1, max_length=255)
    job_type: JobType = JobType.FULL_TIME
    experience_level: Optional[str] = Field(None, max_length=100)
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)
    skills_required: List[str] = Field(default_factory=list)
    fresher_friendly: bool = False
    low_competition: bool = False

    @field_validator("salary_max")
    @classmethod
    def validate_salary_range(cls, v, info):
        salary_min = info.data.get("salary_min")

        if (
            v is not None
            and salary_min is not None
            and v < salary_min
        ):
            raise ValueError(
                "salary_max must be greater than or equal to salary_min"
            )

        return v


class JobUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=255)
    job_type: Optional[JobType] = None
    experience_level: Optional[str] = Field(None, max_length=100)
    salary_min: Optional[Decimal] = Field(None, ge=0)
    salary_max: Optional[Decimal] = Field(None, ge=0)
    skills_required: Optional[List[str]] = None
    fresher_friendly: Optional[bool] = None
    low_competition: Optional[bool] = None
    is_active: Optional[bool] = None


class JobOut(BaseModel):
    """
    Job response schema.

    Existing backend fields are preserved.

    Milestone 3 UI-compatible aliases:
    - skills
    - salary_range
    - company_name

    These are response fields only and do not require database columns.
    """

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    company_id: uuid.UUID

    # Company information
    company_name: Optional[str] = None

    # Core job information
    title: str
    description: str
    location: str
    job_type: JobType

    # Additional job information
    experience_level: Optional[str] = None

    # Salary
    salary_min: Optional[Decimal] = None
    salary_max: Optional[Decimal] = None

    # Original database/API field
    skills_required: List[str] = Field(default_factory=list)

    # ----------------------------------------------------------------------
    # Milestone 3 UI aliases
    # ----------------------------------------------------------------------

    # Frontend can use:
    # current.skills
    skills: List[str] = Field(default_factory=list)

    # Frontend can use:
    # current.salary_range
    salary_range: Optional[str] = None

    # Job flags
    fresher_friendly: bool = False
    low_competition: bool = False

    # Existing metrics
    applicant_count: int
    is_active: bool

    # Timestamps
    posted_at: datetime
    created_at: datetime

    # Dynamic intelligence metrics
    posted_time: str
    competition_level: str


class PaginatedJobsResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    results: List[JobOut]


class CompanyDetailOut(CompanyOut):
    jobs: List[JobOut] = Field(default_factory=list)


# ==========================================================================
# Swipe schemas
# ==========================================================================

class SwipeCreateRequest(BaseModel):
    job_id: uuid.UUID
    action: SwipeAction


class SwipeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    job_id: uuid.UUID
    action: SwipeAction
    created_at: datetime
    updated_at: datetime


class SwipeListResponse(BaseModel):
    total: int
    results: List[SwipeOut]


# ==========================================================================
# Recommendation schemas
# ==========================================================================

class RecommendationItem(BaseModel):
    """
    Existing recommendation contract.

    The actual Job remains nested under `job`.

    The semantic score is included so the AIML/recommendation engine
    can return an actual semantic match value.
    """

    job: JobOut
    match_score: float
    match_reasons: List[str] = Field(default_factory=list)

    semantic_match_score: Optional[float] = None

    recommendation_tags: Optional[List[str]] = None


class RecommendationResponse(BaseModel):
    user_id: uuid.UUID
    generated_at: datetime
    engine: str
    count: int
    recommendations: List[RecommendationItem]


# ==========================================================================
# ATS schemas
# ==========================================================================

class ATSScoreRequest(BaseModel):
    """
    Request sent from the Frontend to the Gateway.
    """

    resume_id: uuid.UUID
    job_id: uuid.UUID


class ATSScoreResponse(BaseModel):
    """
    Existing ATS response fields are preserved.

    Milestone 3 adds detailed scoring dimensions expected by the
    integrated Frontend/AIML contract.
    """

    # Existing field
    match_score: float

    # Detailed ATS dimensions
    overall_score: Optional[float] = None
    skill_score: Optional[float] = None
    keyword_score: Optional[float] = None
    semantic_match_score: Optional[float] = None

    # Explanation
    summary: Optional[str] = None

    # Missing requirements
    missing_skills: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)


class ATSScoreOut(BaseModel):
    """
    AIML/Gateway normalized ATS response.

    This schema directly represents the Milestone 3 UI contract.
    """

    overall_score: float
    skill_score: float
    keyword_score: float
    semantic_match_score: float
    missing_skills: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)


class ATSSuggestion(BaseModel):
    """
    One AI-generated ATS improvement suggestion.
    """

    title: str
    detail: str
    category: Optional[str] = "general"


class ATSSuggestionsOut(BaseModel):
    """
    Collection of AI-generated ATS suggestions.
    """

    suggestions: List[ATSSuggestion]