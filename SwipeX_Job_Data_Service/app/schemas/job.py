from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.models.job import JobType, WorkplaceType, ExperienceLevel, CompetitionLevel
from app.models.company import CompanyType
from app.schemas.company import CompanyOut


class JobBase(BaseModel):
    title: str
    role_category: Optional[str] = None
    description: str
    responsibilities: Optional[str] = None
    requirements: Optional[str] = None
    skills: List[str] = Field(default_factory=list)
    required_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    job_type: JobType = JobType.FULL_TIME
    workplace_type: WorkplaceType = WorkplaceType.HYBRID
    location: str
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    salary_period: str = "Per Annum"
    experience_level: ExperienceLevel = ExperienceLevel.FRESHER
    experience_years_min: int = 0
    experience_years_max: int = 2
    competition_level: CompetitionLevel = CompetitionLevel.MEDIUM
    applicant_count: int = 0
    is_fresher_friendly: bool = True
    is_active: bool = True
    expires_at: Optional[datetime] = None


class JobCreate(JobBase):
    company_id: int


# Output schema matching SRS contract: { job_id, title, company, type, location, salary_range, skills[], posted_at }
# Enhanced with Milestone 2 intelligence indicators: freshness_label, posted_days_ago, is_early_applicant
class JobSummaryOut(BaseModel):
    job_id: int
    title: str
    company: str  # Company Name
    company_id: int
    company_type: CompanyType
    is_newly_founded: bool = False
    company_logo_url: Optional[str] = None
    type: str     # Job Type (Full-time, Internship, etc.)
    workplace_type: str
    location: str
    salary_range: str  # Formatted string e.g. "₹14 LPA - ₹24 LPA"
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: str = "INR"
    skills: List[str]
    required_skills: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    experience_level: str
    competition_level: str
    applicant_count: int
    is_fresher_friendly: bool
    posted_at: datetime
    freshness_label: str = "Active"
    posted_days_ago: int = 0
    is_early_applicant: bool = False

    model_config = ConfigDict(from_attributes=True)


class JobDetailOut(JobBase):
    id: int
    job_id: int  # Alias for API contract consistency
    company: CompanyOut
    salary_range: str
    freshness_label: str = "Active"
    posted_days_ago: int = 0
    is_early_applicant: bool = False
    competition_score: float = 0.0
    posted_at: datetime
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class JobListResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    jobs: List[JobSummaryOut]


# Company detail containing active job listings
class CompanyDetailWithJobsOut(CompanyOut):
    active_jobs_count: int = 0
    jobs: List[JobSummaryOut] = Field(default_factory=list)
