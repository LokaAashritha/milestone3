import os
import sys
import json
import argparse
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base, run_migrations
from app.models import Company, Job, Swipe, SavedJob, Resume, ResumeSkill

BACKUP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backups"))
os.makedirs(BACKUP_DIR, exist_ok=True)


def backup_database(output_file: str = None):
    """
    Exports full database contents to a JSON snapshot backup file.
    Covers Companies, Jobs, Swipes, SavedJobs, Resumes, and ResumeSkills (SRS Day 5).
    """
    db: Session = SessionLocal()
    try:
        if not output_file:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(BACKUP_DIR, f"swipex_backup_m3_{timestamp}.json")

        print(f"Creating database snapshot backup to: {output_file}")

        companies = db.query(Company).all()
        jobs = db.query(Job).all()
        swipes = db.query(Swipe).all()
        saved_jobs = db.query(SavedJob).all()
        resumes = db.query(Resume).all()
        resume_skills = db.query(ResumeSkill).all()

        backup_payload = {
            "metadata": {
                "created_at": datetime.utcnow().isoformat(),
                "service": "SwipeX Job & Data Intelligence Service",
                "version": "Milestone 3",
                "counts": {
                    "companies": len(companies),
                    "jobs": len(jobs),
                    "swipes": len(swipes),
                    "saved_jobs": len(saved_jobs),
                    "resumes": len(resumes),
                    "resume_skills": len(resume_skills)
                }
            },
            "companies": [
                {
                    "id": c.id,
                    "name": c.name,
                    "slug": c.slug,
                    "company_type": c.company_type.value,
                    "is_newly_founded": c.is_newly_founded,
                    "industry": c.industry,
                    "headquarters": c.headquarters,
                    "funding_stage": c.funding_stage,
                    "website": c.website,
                    "description": c.description,
                    "founded_year": c.founded_year,
                    "employee_count_range": c.employee_count_range
                }
                for c in companies
            ],
            "jobs": [
                {
                    "id": j.id,
                    "company_id": j.company_id,
                    "title": j.title,
                    "role_category": j.role_category,
                    "description": j.description,
                    "responsibilities": j.responsibilities,
                    "requirements": j.requirements,
                    "skills": j.skills,
                    "required_skills": j.required_skills,
                    "keywords": j.keywords,
                    "job_type": j.job_type.value,
                    "workplace_type": j.workplace_type.value,
                    "location": j.location,
                    "salary_min": j.salary_min,
                    "salary_max": j.salary_max,
                    "salary_currency": j.salary_currency,
                    "salary_period": j.salary_period,
                    "experience_level": j.experience_level.value,
                    "experience_years_min": j.experience_years_min,
                    "experience_years_max": j.experience_years_max,
                    "competition_level": j.competition_level.value,
                    "applicant_count": j.applicant_count,
                    "is_fresher_friendly": j.is_fresher_friendly,
                    "is_active": j.is_active,
                    "posted_at": j.posted_at.isoformat()
                }
                for j in jobs
            ],
            "swipes": [
                {
                    "id": s.id,
                    "user_id": s.user_id,
                    "job_id": s.job_id,
                    "direction": s.direction.value,
                    "action_type": s.action_type.value,
                    "notes": s.notes,
                    "created_at": s.created_at.isoformat()
                }
                for s in swipes
            ],
            "saved_jobs": [
                {
                    "id": sj.id,
                    "user_id": sj.user_id,
                    "job_id": sj.job_id,
                    "notes": sj.notes,
                    "saved_at": sj.saved_at.isoformat()
                }
                for sj in saved_jobs
            ],
            "resumes": [
                {
                    "id": r.id,
                    "user_id": r.user_id,
                    "file_name": r.file_name,
                    "file_type": r.file_type,
                    "file_size": r.file_size,
                    "file_path": r.file_path,
                    "version_number": r.version_number,
                    "is_active_version": r.is_active_version,
                    "parsed_status": r.parsed_status,
                    "parsed_text": r.parsed_text,
                    "extracted_skills": r.extracted_skills,
                    "uploaded_at": r.uploaded_at.isoformat(),
                    "parsed_at": r.parsed_at.isoformat() if r.parsed_at else None
                }
                for r in resumes
            ],
            "resume_skills": [
                {
                    "id": rs.id,
                    "resume_id": rs.resume_id,
                    "skill_name": rs.skill_name,
                    "category": rs.category,
                    "proficiency_level": rs.proficiency_level,
                    "years_experience": rs.years_experience,
                    "confidence_score": rs.confidence_score,
                    "extracted_at": rs.extracted_at.isoformat()
                }
                for rs in resume_skills
            ]
        }

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(backup_payload, f, indent=2)

        print(f"Backup created successfully! Saved {len(jobs)} jobs, {len(companies)} companies, {len(swipes)} swipes, {len(saved_jobs)} saved jobs, {len(resumes)} resumes, {len(resume_skills)} resume skills.")
        return output_file
    finally:
        db.close()


def restore_database(backup_file: str):
    """
    Restores database tables from a JSON snapshot backup file.
    """
    if not os.path.exists(backup_file):
        raise FileNotFoundError(f"Backup file {backup_file} does not exist.")

    print(f"Restoring database from: {backup_file}")
    with open(backup_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    db: Session = SessionLocal()
    try:
        # Recreate tables and columns
        run_migrations()

        # Clear existing records
        db.query(ResumeSkill).delete()
        db.query(Resume).delete()
        db.query(SavedJob).delete()
        db.query(Swipe).delete()
        db.query(Job).delete()
        db.query(Company).delete()
        db.commit()

        # Restore companies
        for c in data.get("companies", []):
            company = Company(
                id=c["id"],
                name=c["name"],
                slug=c["slug"],
                company_type=c["company_type"],
                is_newly_founded=c.get("is_newly_founded", False),
                industry=c["industry"],
                headquarters=c["headquarters"],
                funding_stage=c.get("funding_stage", "Growth"),
                website=c.get("website"),
                description=c.get("description"),
                founded_year=c.get("founded_year"),
                employee_count_range=c.get("employee_count_range")
            )
            db.add(company)
        db.commit()

        # Restore jobs
        for j in data.get("jobs", []):
            job = Job(
                id=j["id"],
                company_id=j["company_id"],
                title=j["title"],
                role_category=j.get("role_category"),
                description=j["description"],
                responsibilities=j.get("responsibilities"),
                requirements=j.get("requirements"),
                job_type=j["job_type"],
                workplace_type=j["workplace_type"],
                location=j["location"],
                salary_min=j.get("salary_min"),
                salary_max=j.get("salary_max"),
                salary_currency=j.get("salary_currency", "INR"),
                salary_period=j.get("salary_period", "Per Annum"),
                experience_level=j["experience_level"],
                experience_years_min=j.get("experience_years_min", 0),
                experience_years_max=j.get("experience_years_max", 2),
                competition_level=j["competition_level"],
                applicant_count=j.get("applicant_count", 0),
                is_fresher_friendly=j.get("is_fresher_friendly", True),
                is_active=j.get("is_active", True),
                posted_at=datetime.fromisoformat(j["posted_at"])
            )
            job.skills = j.get("skills", [])
            job.required_skills = j.get("required_skills", j.get("skills", []))
            job.keywords = j.get("keywords", [])
            db.add(job)
        db.commit()

        # Restore swipes
        for s in data.get("swipes", []):
            swipe = Swipe(
                id=s["id"],
                user_id=s["user_id"],
                job_id=s["job_id"],
                direction=s["direction"],
                action_type=s["action_type"],
                notes=s.get("notes"),
                created_at=datetime.fromisoformat(s["created_at"])
            )
            db.add(swipe)

        # Restore saved jobs
        for sj in data.get("saved_jobs", []):
            saved = SavedJob(
                id=sj["id"],
                user_id=sj["user_id"],
                job_id=sj["job_id"],
                notes=sj.get("notes"),
                saved_at=datetime.fromisoformat(sj["saved_at"])
            )
            db.add(saved)

        # Restore resumes
        for r in data.get("resumes", []):
            resume = Resume(
                id=r["id"],
                user_id=r["user_id"],
                file_name=r["file_name"],
                file_type=r["file_type"],
                file_size=r.get("file_size", 0),
                file_path=r["file_path"],
                version_number=r.get("version_number", 1),
                is_active_version=r.get("is_active_version", True),
                parsed_status=r.get("parsed_status", "pending"),
                parsed_text=r.get("parsed_text"),
                uploaded_at=datetime.fromisoformat(r["uploaded_at"]),
                parsed_at=datetime.fromisoformat(r["parsed_at"]) if r.get("parsed_at") else None
            )
            resume.extracted_skills = r.get("extracted_skills", [])
            db.add(resume)
        db.commit()

        # Restore resume skills
        for rs in data.get("resume_skills", []):
            r_skill = ResumeSkill(
                id=rs.get("id"),
                resume_id=rs["resume_id"],
                skill_name=rs["skill_name"],
                category=rs.get("category"),
                proficiency_level=rs.get("proficiency_level"),
                years_experience=rs.get("years_experience"),
                confidence_score=rs.get("confidence_score", 1.0),
                extracted_at=datetime.fromisoformat(rs["extracted_at"])
            )
            db.add(r_skill)

        db.commit()
        print("Database restored successfully from snapshot with Milestone 3 tables!")
    except Exception as e:
        db.rollback()
        print(f"Error during restore: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SwipeX Database Backup and Restore Utility")
    parser.add_argument("--backup", action="store_true", help="Create a database backup snapshot")
    parser.add_argument("--restore", type=str, help="Restore database from a specified backup file")
    args = parser.parse_args()

    if args.restore:
        restore_database(args.restore)
    else:
        backup_database()
