"""
app/models.py

Production-ready SQLAlchemy ORM models for the Job Swipe platform.

Entities:
    - User:    Authentication + RBAC subject (Job Seeker / Recruiter / Admin)
    - Company: Employer profile, owns many Jobs
    - Job:     A job posting, owned by a Company, target of Swipes
    - Swipe:   A user's action (apply / save / skip) against a Job
"""

import enum
import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean,
    Enum,
    JSON,
    UniqueConstraint,
    Index,
    Text,
    Numeric,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


# --------------------------------------------------------------------------
# Enums
# --------------------------------------------------------------------------

class UserRole(str, enum.Enum):
    JOB_SEEKER = "job_seeker"
    RECRUITER = "recruiter"
    ADMIN = "admin"


class JobType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"
    REMOTE = "remote"


class SwipeAction(str, enum.Enum):
    APPLY = "apply"
    SAVE = "save"
    SKIP = "skip"


# --------------------------------------------------------------------------
# User
# --------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(
        Enum(
            UserRole,
            name="user_role",
            native_enum=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
        default=UserRole.JOB_SEEKER,
        server_default=UserRole.JOB_SEEKER.value,
    )
    skills = Column(JSON, nullable=False, default=list)  # used by recommendation engine
    is_active = Column(Integer, nullable=False, default=1)  # 1 = active, 0 = disabled
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # A recruiter/admin may own a company profile (nullable for job seekers).
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True)
    company = relationship("Company", back_populates="recruiters", foreign_keys=[company_id])

    swipes = relationship("Swipe", back_populates="user", cascade="all, delete-orphan")
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="user", cascade="all, delete-orphan")
    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email} role={self.role}>"


# --------------------------------------------------------------------------
# Company
# --------------------------------------------------------------------------

class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    about = Column(Text, nullable=True)
    industry = Column(String(150), nullable=True, index=True)
    location = Column(String(255), nullable=True, index=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    jobs = relationship("Job", back_populates="company", cascade="all, delete-orphan")
    recruiters = relationship("User", back_populates="company", foreign_keys="User.company_id")

    def __repr__(self) -> str:
        return f"<Company id={self.id} name={self.name}>"


# --------------------------------------------------------------------------
# Job
# --------------------------------------------------------------------------

class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    posted_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=False)
    location = Column(String(255), nullable=False, index=True)
    job_type = Column(
        Enum(
            JobType,
            name="job_type",
            native_enum=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
        default=JobType.FULL_TIME,
        server_default=JobType.FULL_TIME.value,
    )
    experience_level = Column(String(100), nullable=True, index=True)
    salary_min = Column(Numeric(12, 2), nullable=True)
    salary_max = Column(Numeric(12, 2), nullable=True)
    skills_required = Column(JSON, nullable=False, default=list)  # e.g. ["Python", "SQL"]
    fresher_friendly = Column(Boolean, nullable=False, default=False, server_default="false", index=True)
    low_competition = Column(Boolean, nullable=False, default=False, server_default="false", index=True)
    applicant_count = Column(Integer, nullable=False, default=0, server_default="0")
    is_active = Column(Integer, nullable=False, default=1)  # 1 = open, 0 = closed
    posted_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    company = relationship("Company", back_populates="jobs")
    swipes = relationship("Swipe", back_populates="job", cascade="all, delete-orphan")
    saved_jobs = relationship("SavedJob", back_populates="job", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_jobs_location_type", "location", "job_type"),
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title}>"


# --------------------------------------------------------------------------
# Swipe
# --------------------------------------------------------------------------

class Swipe(Base):
    __tablename__ = "swipes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    action = Column(
        Enum(
            SwipeAction,
            name="swipe_action",
            native_enum=True,
            values_callable=lambda enum_type: [item.value for item in enum_type],
        ),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    user = relationship("User", back_populates="swipes")
    job = relationship("Job", back_populates="swipes")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_swipe_user_job"),
    )

    def __repr__(self) -> str:
        return f"<Swipe user_id={self.user_id} job_id={self.job_id} action={self.action}>"


class SavedJob(Base):
    __tablename__ = "saved_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="saved_jobs")
    job = relationship("Job", back_populates="saved_jobs")

    __table_args__ = (
        UniqueConstraint("user_id", "job_id", name="uq_saved_job_user_job"),
    )

# --------------------------------------------------------------------------
# Resume (Milestone 3 - Day 2)
# --------------------------------------------------------------------------

class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)  # 'pdf' or 'docx'
    version_number = Column(Integer, nullable=False, default=1)
    is_active_version = Column(Boolean, nullable=False, default=True, server_default="true")
    parsed_status = Column(String(20), nullable=False, default="pending")  # 'pending', 'processing', 'done', 'failed'
    parsed_text = Column(Text, nullable=True)
    extracted_skills = Column(JSON, nullable=True)  # e.g. ["Python", "FastAPI", "Docker"]
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User", back_populates="resumes")

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user_id={self.user_id} version={self.version_number}>"