import json
import uuid
from datetime import datetime
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from app.models.resume import Resume, ResumeSkill, ParsedStatus
from app.models.job import Job
from app.core.storage import storage_manager


class ResumeService:
    """
    Core repository and query layer for Resume versioning, storage,
    skill-matching queries, and ATS score computations.
    """

    @staticmethod
    def get_next_version_number(db: Session, user_id: str) -> int:
        """Determines the next incremental version number for a user's resume."""
        max_version = db.query(func.max(Resume.version_number)).filter(Resume.user_id == str(user_id)).scalar()
        return (max_version or 0) + 1

    @classmethod
    def create_resume_version(
        cls,
        db: Session,
        user_id: str,
        filename: str,
        content: bytes,
        is_active: bool = True
    ) -> Resume:
        """
        Uploads and creates a new resume version for the user.
        Preserves all past versions while marking the new one active if requested.
        """
        version_num = cls.get_next_version_number(db, user_id)
        
        # Save file to secure user directory
        file_path, file_type, file_size, _ = storage_manager.save_resume_file(
            user_id=user_id,
            original_filename=filename,
            content=content,
            version_number=version_num
        )

        # If this new version is active, deactivate all previous versions
        if is_active:
            db.query(Resume).filter(
                Resume.user_id == str(user_id),
                Resume.is_active_version == True
            ).update({"is_active_version": False})

        resume_id = str(uuid.uuid4())
        resume = Resume(
            id=resume_id,
            user_id=str(user_id),
            file_name=filename,
            file_type=file_type,
            file_size=file_size,
            file_path=file_path,
            version_number=version_num,
            is_active_version=is_active,
            parsed_status=ParsedStatus.PENDING.value,
            parsed_text=None,
            _extracted_skills="[]",
            uploaded_at=datetime.utcnow()
        )
        db.add(resume)
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def list_user_resumes(
        db: Session, user_id: str, active_only: bool = False
    ) -> List[Resume]:
        """Lists user's resume versions, sorted newest first."""
        query = db.query(Resume).filter(Resume.user_id == str(user_id))
        if active_only:
            query = query.filter(Resume.is_active_version == True)
        return query.order_by(desc(Resume.uploaded_at)).all()

    @staticmethod
    def get_user_resume(
        db: Session, resume_id: str, user_id: str
    ) -> Resume:
        """
        Fetches resume with strict user ownership validation.
        Returns 404 if resume does not exist OR belongs to another user (FR-09 security).
        """
        resume = db.query(Resume).filter(
            Resume.id == str(resume_id),
            Resume.user_id == str(user_id)
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )
        return resume

    @staticmethod
    def set_active_version(
        db: Session, user_id: str, resume_id: str
    ) -> Resume:
        """Sets the specified resume version as the default/active resume."""
        resume = db.query(Resume).filter(
            Resume.id == str(resume_id),
            Resume.user_id == str(user_id)
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        # Deactivate all others
        db.query(Resume).filter(
            Resume.user_id == str(user_id)
        ).update({"is_active_version": False})

        resume.is_active_version = True
        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def save_parsed_results(
        db: Session,
        resume_id: str,
        user_id: str,
        parsed_text: str,
        extracted_skills: List[str]
    ) -> Resume:
        """
        Stores parsed text and extracted skills, updating status to 'done'.
        Populates both the denormalized JSON column and normalized ResumeSkill rows.
        """
        resume = db.query(Resume).filter(
            Resume.id == str(resume_id),
            Resume.user_id == str(user_id)
        ).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found"
            )

        resume.parsed_text = parsed_text
        resume.extracted_skills = extracted_skills
        resume.parsed_status = ParsedStatus.DONE.value
        resume.parsed_at = datetime.utcnow()

        # Delete any prior skills for this resume to avoid duplicates
        db.query(ResumeSkill).filter(ResumeSkill.resume_id == str(resume_id)).delete()

        # Add normalized records
        for skill in extracted_skills:
            clean_skill = skill.strip()
            if clean_skill:
                rs = ResumeSkill(
                    resume_id=str(resume_id),
                    skill_name=clean_skill,
                    confidence_score=1.0,
                    extracted_at=datetime.utcnow()
                )
                db.add(rs)

        db.commit()
        db.refresh(resume)
        return resume

    @staticmethod
    def compute_ats_score(
        resume: Resume, job: Job
    ) -> Dict[str, Any]:
        """
        Computes ATS compatibility score comparing resume's extracted skills & text
        against job's required_skills and domain keywords.
        
        Strict Contract Rule (FR-04):
        - If match_score < 80%: missing_skills and missing_keywords are populated.
        - If match_score >= 80%: both are returned as empty lists [].
        """
        if resume.parsed_status != ParsedStatus.DONE.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Resume is not yet parsed. Please trigger parsing first."
            )

        resume_skills_lower = {s.strip().lower() for s in (resume.extracted_skills or [])}
        job_req_skills = job.required_skills or job.skills or []
        job_keywords = job.keywords or []

        # Compare required skills
        matched_skills = []
        missing_skills = []
        for req in job_req_skills:
            if req.strip().lower() in resume_skills_lower:
                matched_skills.append(req)
            else:
                missing_skills.append(req)

        skill_ratio = len(matched_skills) / len(job_req_skills) if job_req_skills else 1.0

        # Compare domain keywords against parsed resume text or skills
        parsed_text_lower = (resume.parsed_text or "").lower()
        matched_keywords = []
        missing_keywords = []
        for kw in job_keywords:
            kw_clean = kw.strip().lower()
            if kw_clean in resume_skills_lower or kw_clean in parsed_text_lower:
                matched_keywords.append(kw)
            else:
                missing_keywords.append(kw)

        keyword_ratio = len(matched_keywords) / len(job_keywords) if job_keywords else 1.0

        # Blended ATS score (70% required skills match + 30% domain keyword relevance)
        raw_score = (skill_ratio * 70.0) + (keyword_ratio * 30.0)
        match_score = round(min(100.0, max(0.0, raw_score)), 1)

        # Enforce FR-04 threshold rule
        if match_score >= 80.0:
            final_missing_skills: List[str] = []
            final_missing_keywords: List[str] = []
        else:
            final_missing_skills = missing_skills
            final_missing_keywords = missing_keywords

        return {
            "resume_id": str(resume.id),
            "job_id": str(job.id),
            "match_score": match_score,
            "missing_skills": final_missing_skills,
            "missing_keywords": final_missing_keywords,
            "scored_at": datetime.utcnow().isoformat() + "Z"
        }
