import json
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.core.intelligence import compute_job_freshness, compute_competition_level


class JobType(str, Enum):
    FULL_TIME = "Full-time"
    PART_TIME = "Part-time"
    INTERNSHIP = "Internship"
    CONTRACT = "Contract"


class WorkplaceType(str, Enum):
    REMOTE = "Remote"
    ON_SITE = "On-site"
    HYBRID = "Hybrid"


class ExperienceLevel(str, Enum):
    FRESHER = "Fresher"
    ENTRY = "Entry-level"
    MID = "Mid-level"
    SENIOR = "Senior"
    LEAD = "Lead"


class CompetitionLevel(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, index=True)
    role_category = Column(String(100), nullable=True, index=True)
    description = Column(Text, nullable=False)
    responsibilities = Column(Text, nullable=True)
    requirements = Column(Text, nullable=True)
    
    # Skills stored as JSON serialized string
    _skills = Column("skills", Text, nullable=False, default="[]")
    
    # Milestone 3: Structured required_skills & domain keywords for ATS scoring & matching
    _required_skills = Column("required_skills", Text, nullable=True, default="[]")
    _keywords = Column("keywords", Text, nullable=True, default="[]")
    
    job_type = Column(
        SQLEnum(JobType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=JobType.FULL_TIME,
        nullable=False,
        index=True
    )
    workplace_type = Column(
        SQLEnum(WorkplaceType, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=WorkplaceType.HYBRID,
        nullable=False,
        index=True
    )
    location = Column(String(255), nullable=False, index=True)
    
    # Compensation
    salary_min = Column(Integer, nullable=True, index=True)
    salary_max = Column(Integer, nullable=True, index=True)
    salary_currency = Column(String(10), default="INR", nullable=False)
    salary_period = Column(String(20), default="Per Annum", nullable=False)
    
    # Career intelligence fields
    experience_level = Column(
        SQLEnum(ExperienceLevel, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=ExperienceLevel.FRESHER,
        nullable=False,
        index=True
    )
    experience_years_min = Column(Integer, default=0, nullable=False)
    experience_years_max = Column(Integer, default=2, nullable=False)
    
    competition_level = Column(
        SQLEnum(CompetitionLevel, values_callable=lambda x: [e.value for e in x], native_enum=False),
        default=CompetitionLevel.MEDIUM,
        nullable=False,
        index=True
    )
    applicant_count = Column(Integer, default=0, nullable=False, index=True)
    is_fresher_friendly = Column(Boolean, default=True, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=True)

    # Composite indexes for fast multi-criteria filtering
    __table_args__ = (
        Index("ix_jobs_type_location", "job_type", "location"),
        Index("ix_jobs_salary_range", "salary_min", "salary_max"),
        Index("ix_jobs_exp_competition", "experience_level", "competition_level"),
    )

    # Relationships
    company = relationship("Company", back_populates="jobs")
    swipes = relationship("Swipe", back_populates="job", cascade="all, delete-orphan")
    saved_by_users = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")

    @property
    def skills(self) -> List[str]:
        try:
            return json.loads(self._skills) if self._skills else []
        except Exception:
            return []

    @skills.setter
    def skills(self, val: List[str]):
        self._skills = json.dumps(val)

    @property
    def required_skills(self) -> List[str]:
        try:
            return json.loads(self._required_skills) if self._required_skills else self.skills
        except Exception:
            return self.skills

    @required_skills.setter
    def required_skills(self, val: List[str]):
        self._required_skills = json.dumps(val if val is not None else [])

    @property
    def keywords(self) -> List[str]:
        try:
            return json.loads(self._keywords) if self._keywords else []
        except Exception:
            return []

    @keywords.setter
    def keywords(self, val: List[str]):
        self._keywords = json.dumps(val if val is not None else [])

    @property
    def freshness_info(self) -> dict:
        return compute_job_freshness(self.posted_at)

    @property
    def competition_info(self) -> dict:
        return compute_competition_level(self.applicant_count)

    def __repr__(self):
        return f"<Job(id={self.id}, title='{self.title}', company_id={self.company_id})>"
