import os
import sys
import csv
import json
import random
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.company import Company, CompanyType
from app.models.job import (
    Job, JobType, WorkplaceType, ExperienceLevel, CompetitionLevel
)
from app.models.swipe import Swipe, SwipeDirection, SwipeActionType
from app.models.saved_job import SavedJob
from app.models.resume import Resume, ResumeSkill, ParsedStatus

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data"))
COMPANIES_CSV = os.path.join(DATA_DIR, "companies_dataset.csv")
JOBS_CSV = os.path.join(DATA_DIR, "jobs_dataset.csv")

KEYWORDS_FALLBACK_MAP = {
    "Backend": ["RESTful APIs", "Microservices", "Docker", "CI/CD", "PostgreSQL", "Database Optimization", "Scalability"],
    "Frontend": ["Responsive Design", "State Management", "Component Architecture", "Accessibility", "Tailwind CSS", "TypeScript"],
    "Full Stack": ["REST APIs", "Full Stack Architecture", "Docker", "SQL", "Frontend Integration", "System Design"],
    "AI/ML": ["Machine Learning", "NLP", "Vector Search", "Embeddings", "LLMs", "Deep Learning", "Transformers"],
    "Data Analytics": ["Data Analysis", "SQL Queries", "ETL", "Dashboarding", "Statistical Analysis", "Business Intelligence"],
    "QA/Testing": ["Test Automation", "Pytest", "Integration Testing", "Regression Testing", "API Testing", "CI/CD"],
    "Design": ["User Research", "Wireframing", "Interactive Prototyping", "Design Systems", "Figma", "Usability Testing"],
    "Mobile": ["Mobile Architecture", "iOS", "Android", "Cross-Platform", "App Performance", "Offline Storage"],
    "DevOps": ["Kubernetes", "Docker", "CI/CD Pipelines", "Terraform", "Infrastructure as Code", "Monitoring"]
}


def backfill_jobs_m3_fields(db: Session):
    """
    Backfills structured required_skills and domain keywords for all existing jobs in DB (SRS Day 3).
    """
    jobs = db.query(Job).all()
    count = 0
    for j in jobs:
        needs_update = False
        if not j._required_skills or j._required_skills == "[]":
            j.required_skills = j.skills
            needs_update = True
        if not j._keywords or j._keywords == "[]":
            j.keywords = KEYWORDS_FALLBACK_MAP.get(j.role_category, ["Agile", "Git", "Problem Solving", "Software Engineering"])
            needs_update = True
        if needs_update:
            count += 1
    if count > 0:
        db.commit()
        print(f"Backfilled M3 required_skills & keywords for {count} jobs.")


def seed_sample_resumes(db: Session):
    """
    Seeds sample uploaded resumes and extracted skills matching Aashritha's API contracts.
    """
    existing_resumes = db.query(Resume).count()
    if existing_resumes > 0:
        return

    sample_user_id = "4f9c2e3d-1111-4444-8888-123456789abc"
    r1 = Resume(
        id="b1a2c3d4-0000-4444-8888-abcdefabcdef",
        user_id=sample_user_id,
        file_name="asha_resume_v3.pdf",
        file_type="pdf",
        file_size=245760,
        file_path="./uploads/resumes/4f9c2e3d-1111-4444-8888-123456789abc/asha_resume_v3.pdf",
        version_number=3,
        is_active_version=True,
        parsed_status=ParsedStatus.DONE.value,
        parsed_text="Experienced Software Engineer with proficiency in Python, FastAPI, PostgreSQL, Docker, and REST APIs. Built microservices and CI/CD pipelines.",
        uploaded_at=datetime.utcnow() - timedelta(days=2),
        parsed_at=datetime.utcnow() - timedelta(days=2, minutes=5)
    )
    r1.extracted_skills = ["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs", "SQL", "Git"]
    db.add(r1)

    r2 = Resume(
        id="a0e1c2d3-1111-4444-8888-111122223333",
        user_id=sample_user_id,
        file_name="asha_resume_v2.pdf",
        file_type="pdf",
        file_size=198400,
        file_path="./uploads/resumes/4f9c2e3d-1111-4444-8888-123456789abc/asha_resume_v2.pdf",
        version_number=2,
        is_active_version=False,
        parsed_status=ParsedStatus.DONE.value,
        parsed_text="Software Developer specializing in Python and basic REST APIs.",
        uploaded_at=datetime.utcnow() - timedelta(days=15),
        parsed_at=datetime.utcnow() - timedelta(days=15, minutes=3)
    )
    r2.extracted_skills = ["Python", "REST APIs", "Git"]
    db.add(r2)

    db.commit()

    # Add normalized resume skills for r1
    for sk in r1.extracted_skills:
        rs = ResumeSkill(
            resume_id=r1.id,
            skill_name=sk,
            confidence_score=0.95,
            extracted_at=datetime.utcnow()
        )
        db.add(rs)
    db.commit()
    print("Seeded sample resumes and resume_skills for testing.")


def seed_database(db: Session = None):
    """
    Ingests and seeds the database using the CSV dataset files in data/
    Populates Companies, Jobs, Swipes, SavedJobs, Resumes, and ResumeSkills.
    """
    close_after = False
    if db is None:
        Base.metadata.create_all(bind=engine)
        db = SessionLocal()
        close_after = True

    try:
        # Check if already seeded
        existing_companies = db.query(Company).count()
        if existing_companies > 0:
            print(f"Database already contains {existing_companies} companies.")
            backfill_jobs_m3_fields(db)
            seed_sample_resumes(db)
            return

        print(f"Ingesting datasets from {DATA_DIR} into database...")
        
        # 1. Ingest Companies CSV
        company_map = {}
        if os.path.exists(COMPANIES_CSV):
            with open(COMPANIES_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    c_type = CompanyType(row["company_type"])
                    is_new = row.get("is_newly_founded", "False").lower() == "true"
                    company = Company(
                        name=row["name"],
                        slug=row["slug"],
                        company_type=c_type,
                        is_newly_founded=is_new,
                        industry=row["industry"],
                        headquarters=row["headquarters"],
                        funding_stage=row.get("funding_stage", "Growth"),
                        website=row["website"],
                        founded_year=int(row["founded_year"]) if row["founded_year"] else None,
                        employee_count_range=row["employee_count_range"]
                    )
                    db.add(company)
                    db.flush()
                    company_map[row["name"]] = company.id
            db.commit()
            print(f"Ingested {len(company_map)} companies from CSV.")
        else:
            print(f"Warning: {COMPANIES_CSV} not found.")

        # 2. Ingest Jobs CSV
        jobs_created = []
        if os.path.exists(JOBS_CSV):
            with open(JOBS_CSV, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    comp_id = company_map.get(row["company_name"])
                    if not comp_id:
                        continue

                    # Parse dates
                    try:
                        posted_at = datetime.strptime(row["posted_at"], "%Y-%m-%d %H:%M:%S")
                    except Exception:
                        posted_at = datetime.utcnow()

                    # Parse skills list
                    try:
                        skills_list = json.loads(row["skills_required"])
                    except Exception:
                        skills_list = [s.strip() for s in row["skills_required"].split(",") if s.strip()]

                    # Parse required_skills & keywords
                    try:
                        req_skills = json.loads(row.get("required_skills", "[]")) or skills_list
                    except Exception:
                        req_skills = skills_list

                    try:
                        keywords_list = json.loads(row.get("keywords", "[]"))
                    except Exception:
                        keywords_list = KEYWORDS_FALLBACK_MAP.get(row.get("role_category", "Technology"), ["Agile", "Git", "Problem Solving"])

                    job = Job(
                        company_id=comp_id,
                        title=row["job_title"],
                        role_category=row.get("role_category", "Technology"),
                        description=row["job_description"],
                        responsibilities=row.get("responsibilities", ""),
                        requirements=row.get("requirements", ""),
                        job_type=JobType(row["job_type"]),
                        workplace_type=WorkplaceType(row["workplace_type"]),
                        location=row["location"],
                        salary_min=int(row["salary_min"]) if row["salary_min"] else None,
                        salary_max=int(row["salary_max"]) if row["salary_max"] else None,
                        salary_currency=row.get("salary_currency", "INR"),
                        salary_period=row.get("salary_period", "Per Annum"),
                        experience_level=ExperienceLevel(row["experience_level"]),
                        experience_years_min=int(row["experience_years_min"]) if row.get("experience_years_min") else 0,
                        experience_years_max=int(row["experience_years_max"]) if row.get("experience_years_max") else 2,
                        competition_level=CompetitionLevel(row["competition_level"]),
                        applicant_count=int(row["applicant_count"]) if row.get("applicant_count") else 0,
                        is_fresher_friendly=row.get("is_fresher_friendly", "True").lower() == "true",
                        is_active=True,
                        posted_at=posted_at
                    )
                    job.skills = skills_list
                    job.required_skills = req_skills
                    job.keywords = keywords_list
                    db.add(job)
                    jobs_created.append(job)

            db.commit()
            print(f"Ingested {len(jobs_created)} jobs from CSV into database.")

        # 3. Insert sample user swipe interactions
        if jobs_created:
            now = datetime.utcnow()
            sample_swipes = [
                {"user_id": "demo-user-1", "job_id": jobs_created[0].id, "direction": SwipeDirection.RIGHT, "action": SwipeActionType.APPLY},
                {"user_id": "demo-user-1", "job_id": jobs_created[1].id, "direction": SwipeDirection.RIGHT, "action": SwipeActionType.SAVE},
                {"user_id": "demo-user-1", "job_id": jobs_created[2].id, "direction": SwipeDirection.LEFT, "action": SwipeActionType.SKIP},
                {"user_id": "demo-user-1", "job_id": jobs_created[3].id, "direction": SwipeDirection.RIGHT, "action": SwipeActionType.APPLY},
                {"user_id": "demo-user-1", "job_id": jobs_created[4].id, "direction": SwipeDirection.LEFT, "action": SwipeActionType.SKIP},
                {"user_id": "candidate-jane", "job_id": jobs_created[0].id, "direction": SwipeDirection.RIGHT, "action": SwipeActionType.APPLY},
                {"user_id": "candidate-jane", "job_id": jobs_created[5].id, "direction": SwipeDirection.RIGHT, "action": SwipeActionType.SAVE},
            ]

            for s in sample_swipes:
                swipe = Swipe(
                    user_id=s["user_id"],
                    job_id=s["job_id"],
                    direction=s["direction"],
                    action_type=s["action"],
                    created_at=now - timedelta(hours=random.randint(2, 48))
                )
                db.add(swipe)

            # 4. Insert sample saved jobs
            sample_saved = [
                {"user_id": "demo-user-1", "job_id": jobs_created[1].id, "notes": "High priority: Python backend role at scale-up startup"},
                {"user_id": "demo-user-1", "job_id": jobs_created[5].id, "notes": "Generative AI role - review portfolio before applying"},
                {"user_id": "candidate-jane", "job_id": jobs_created[2].id, "notes": "Check remote flexibility and relocation stipend"},
            ]
            for sv in sample_saved:
                saved_job = SavedJob(
                    user_id=sv["user_id"],
                    job_id=sv["job_id"],
                    notes=sv["notes"],
                    saved_at=now - timedelta(hours=random.randint(1, 24))
                )
                db.add(saved_job)

            db.commit()
            print(f"Inserted {len(sample_swipes)} swipes and {len(sample_saved)} saved jobs.")

        # 5. Seed sample resumes
        seed_sample_resumes(db)
        print("Dataset ingestion and database seeding completed successfully!")

    except Exception as e:
        db.rollback()
        print(f"Error during dataset ingestion: {e}")
        raise e
    finally:
        if close_after:
            db.close()


if __name__ == "__main__":
    seed_database()
