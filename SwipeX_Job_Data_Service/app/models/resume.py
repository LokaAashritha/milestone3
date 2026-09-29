import json
import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Float, Enum as SQLEnum
)
from sqlalchemy.orm import relationship
from app.core.database import Base


class ParsedStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class Resume(Base):
    __tablename__ = "resumes"

    # UUID string primary key to match backend & frontend contract
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(String(36), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # pdf, docx
    file_size = Column(Integer, nullable=False, default=0)
    file_path = Column(String(500), nullable=False)
    version_number = Column(Integer, nullable=False, default=1)
    is_active_version = Column(Boolean, nullable=False, default=True, index=True)
    
    parsed_status = Column(
        String(50),
        nullable=False,
        default=ParsedStatus.PENDING.value,
        index=True
    )
    parsed_text = Column(Text, nullable=True)
    _extracted_skills = Column("extracted_skills", Text, nullable=True, default="[]")
    
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    parsed_at = Column(DateTime, nullable=True)

    # Relationships
    skills_rel = relationship("ResumeSkill", back_populates="resume", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_resumes_user_version", "user_id", "version_number"),
        Index("ix_resumes_user_active", "user_id", "is_active_version"),
    )

    @property
    def extracted_skills(self) -> List[str]:
        try:
            return json.loads(self._extracted_skills) if self._extracted_skills else []
        except Exception:
            return []

    @extracted_skills.setter
    def extracted_skills(self, val: List[str]):
        self._extracted_skills = json.dumps(val if val is not None else [])

    def __repr__(self):
        return f"<Resume(id='{self.id}', user_id='{self.user_id}', file_name='{self.file_name}', v={self.version_number}, status='{self.parsed_status}')>"


class ResumeSkill(Base):
    __tablename__ = "resume_skills"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    resume_id = Column(String(36), ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True)
    skill_name = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=True, index=True)
    proficiency_level = Column(String(50), nullable=True)  # Beginner, Intermediate, Expert
    years_experience = Column(Float, nullable=True)
    confidence_score = Column(Float, default=1.0, nullable=False)
    extracted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    resume = relationship("Resume", back_populates="skills_rel")

    __table_args__ = (
        Index("ix_resume_skills_name", "skill_name"),
        Index("ix_resume_skills_resume_skill", "resume_id", "skill_name"),
    )

    def __repr__(self):
        return f"<ResumeSkill(resume_id='{self.resume_id}', skill='{self.skill_name}', confidence={self.confidence_score})>"
