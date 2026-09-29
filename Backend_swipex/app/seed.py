"""
app/seed.py

Populates the database with dummy companies, jobs, and test users so the
application is immediately usable after installation, without requiring
any manual data entry.

Run with:
    python app/seed.py

Idempotent: running it multiple times will not create duplicate rows —
it checks for existing records (by unique email / company name) first.
"""

import sys
import os
import random
from datetime import datetime, timedelta, timezone

# Allow running this file directly as `python app/seed.py`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, init_db
from app.models import User, Company, Job, Swipe, UserRole, JobType, SwipeAction
from app.auth import hash_password


TEST_PASSWORD = "Password123"


def seed_users(db):
    users_spec = [
        {
            "email": "admin@jobswipe.dev",
            "full_name": "Ava Administrator",
            "role": UserRole.ADMIN,
            "skills": [],
        },
        {
            "email": "recruiter@jobswipe.dev",
            "full_name": "Raj Recruiter",
            "role": UserRole.RECRUITER,
            "skills": [],
        },
        {
            "email": "recruiter2@jobswipe.dev",
            "full_name": "Nina Talent",
            "role": UserRole.RECRUITER,
            "skills": [],
        },
        {
            "email": "jobseeker@jobswipe.dev",
            "full_name": "Sam Seeker",
            "role": UserRole.JOB_SEEKER,
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker"],
        },
        {
            "email": "jobseeker2@jobswipe.dev",
            "full_name": "Priya Coder",
            "role": UserRole.JOB_SEEKER,
            "skills": ["JavaScript", "React", "Node.js", "AWS"],
        },
        {
            "email": "jobseeker3@jobswipe.dev",
            "full_name": "Diego Designer",
            "role": UserRole.JOB_SEEKER,
            "skills": ["Figma", "UI Design", "User Research"],
        },
    ]

    created = {}
    for spec in users_spec:
        existing = db.query(User).filter(User.email == spec["email"]).first()
        if existing:
            created[spec["email"]] = existing
            continue
        user = User(
            email=spec["email"],
            password_hash=hash_password(TEST_PASSWORD),
            full_name=spec["full_name"],
            role=spec["role"],
            skills=spec["skills"],
        )
        db.add(user)
        db.flush()
        created[spec["email"]] = user

    db.commit()
    return created


def seed_companies(db, recruiter_users):
    companies_spec = [
        {
            "name": "NimbusTech Solutions",
            "about": "Cloud infrastructure and DevOps platform provider serving mid-market SaaS companies.",
            "industry": "Cloud Computing",
            "location": "Austin, TX",
            "website": "https://nimbustech.example.com",
        },
        {
            "name": "BrightPath Analytics",
            "about": "Data analytics and business intelligence consultancy helping enterprises make sense of their data.",
            "industry": "Data & Analytics",
            "location": "New York, NY",
            "website": "https://brightpath.example.com",
        },
        {
            "name": "GreenLeaf Foods",
            "about": "Sustainable food-tech company building the next generation of plant-based logistics software.",
            "industry": "Food Technology",
            "location": "Portland, OR",
            "website": "https://greenleaf.example.com",
        },
        {
            "name": "PixelForge Studios",
            "about": "Independent game studio and creative agency crafting immersive interactive experiences.",
            "industry": "Gaming & Entertainment",
            "location": "Remote",
            "website": "https://pixelforge.example.com",
        },
    ]

    created = []
    for spec in companies_spec:
        existing = db.query(Company).filter(Company.name == spec["name"]).first()
        if existing:
            created.append(existing)
            continue
        company = Company(**spec)
        db.add(company)
        db.flush()
        created.append(company)

    db.commit()

    # Attach recruiters to companies (idempotent)
    recruiter1 = recruiter_users.get("recruiter@jobswipe.dev")
    recruiter2 = recruiter_users.get("recruiter2@jobswipe.dev")
    if recruiter1 and recruiter1.company_id is None and created:
        recruiter1.company_id = created[0].id
    if recruiter2 and recruiter2.company_id is None and len(created) > 1:
        recruiter2.company_id = created[1].id
    db.commit()

    return created


def seed_jobs(db, companies, recruiter_users):
    if db.query(Job).count() > 0:
        return db.query(Job).all()

    recruiter1 = recruiter_users.get("recruiter@jobswipe.dev")
    recruiter2 = recruiter_users.get("recruiter2@jobswipe.dev")

    now = datetime.now(timezone.utc)

    jobs_spec = [
        {
            "company": companies[0],
            "posted_by": recruiter1,
            "title": "Senior Backend Engineer (Python)",
            "description": (
                "Design and build scalable microservices powering our cloud platform. "
                "You'll work extensively with FastAPI, PostgreSQL, and Kubernetes."
            ),
            "location": "Austin, TX",
            "job_type": JobType.FULL_TIME,
            "salary_min": 130000,
            "salary_max": 170000,
            "skills_required": ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
            "applicant_count": 4,
            "posted_at": now - timedelta(hours=6),
        },
        {
            "company": companies[0],
            "posted_by": recruiter1,
            "title": "DevOps Engineer",
            "description": "Own our CI/CD pipelines and cloud infrastructure across AWS and GCP.",
            "location": "Remote",
            "job_type": JobType.REMOTE,
            "salary_min": 115000,
            "salary_max": 150000,
            "skills_required": ["AWS", "Terraform", "Docker", "CI/CD"],
            "applicant_count": 12,
            "posted_at": now - timedelta(days=2),
        },
        {
            "company": companies[1],
            "posted_by": recruiter2,
            "title": "Data Analyst",
            "description": "Turn raw data into actionable insights for our enterprise clients using SQL and Python.",
            "location": "New York, NY",
            "job_type": JobType.FULL_TIME,
            "salary_min": 85000,
            "salary_max": 105000,
            "skills_required": ["SQL", "Python", "Tableau", "Excel"],
            "applicant_count": 55,
            "posted_at": now - timedelta(days=10),
        },
        {
            "company": companies[1],
            "posted_by": recruiter2,
            "title": "Machine Learning Engineer",
            "description": "Build predictive models and deploy them into production analytics pipelines.",
            "location": "New York, NY",
            "job_type": JobType.FULL_TIME,
            "salary_min": 140000,
            "salary_max": 180000,
            "skills_required": ["Python", "Machine Learning", "TensorFlow", "SQL"],
            "applicant_count": 8,
            "posted_at": now - timedelta(hours=20),
        },
        {
            "company": companies[2],
            "posted_by": None,
            "title": "Full-Stack Developer (React/Node.js)",
            "description": "Build customer-facing web applications for our sustainable food logistics platform.",
            "location": "Portland, OR",
            "job_type": JobType.FULL_TIME,
            "salary_min": 100000,
            "salary_max": 135000,
            "skills_required": ["JavaScript", "React", "Node.js", "PostgreSQL"],
            "applicant_count": 22,
            "posted_at": now - timedelta(days=5),
        },
        {
            "company": companies[2],
            "posted_by": None,
            "title": "Supply Chain Intern",
            "description": "Support our operations team in analyzing and optimizing plant-based supply chains.",
            "location": "Portland, OR",
            "job_type": JobType.INTERNSHIP,
            "salary_min": 25,
            "salary_max": 30,
            "skills_required": ["Excel", "Data Analysis"],
            "applicant_count": 3,
            "posted_at": now - timedelta(days=1),
        },
        {
            "company": companies[3],
            "posted_by": None,
            "title": "UI/UX Designer",
            "description": "Design intuitive, delightful interfaces for our upcoming mobile game titles.",
            "location": "Remote",
            "job_type": JobType.CONTRACT,
            "salary_min": 70000,
            "salary_max": 95000,
            "skills_required": ["Figma", "UI Design", "User Research", "Prototyping"],
            "applicant_count": 9,
            "posted_at": now - timedelta(days=30),
        },
        {
            "company": companies[3],
            "posted_by": None,
            "title": "Gameplay Programmer",
            "description": "Implement core gameplay systems using our proprietary engine and tooling.",
            "location": "Remote",
            "job_type": JobType.FULL_TIME,
            "salary_min": 95000,
            "salary_max": 125000,
            "skills_required": ["C++", "Game Development", "Python"],
            "applicant_count": 61,
            "posted_at": now - timedelta(days=45),
        },
    ]

    created_jobs = []
    for spec in jobs_spec:
        job = Job(
            company_id=spec["company"].id,
            posted_by=spec["posted_by"].id if spec["posted_by"] else None,
            title=spec["title"],
            description=spec["description"],
            location=spec["location"],
            job_type=spec["job_type"],
            salary_min=spec["salary_min"],
            salary_max=spec["salary_max"],
            skills_required=spec["skills_required"],
            applicant_count=spec["applicant_count"],
            posted_at=spec["posted_at"],
        )
        db.add(job)
        created_jobs.append(job)

    db.commit()
    for job in created_jobs:
        db.refresh(job)
    return created_jobs


def seed_swipes(db, users, jobs):
    if db.query(Swipe).count() > 0:
        return

    seeker1 = users.get("jobseeker@jobswipe.dev")
    seeker2 = users.get("jobseeker2@jobswipe.dev")

    if seeker1 and jobs:
        db.add(Swipe(user_id=seeker1.id, job_id=jobs[0].id, action=SwipeAction.APPLY))
        db.add(Swipe(user_id=seeker1.id, job_id=jobs[3].id, action=SwipeAction.SAVE))
        if len(jobs) > 6:
            db.add(Swipe(user_id=seeker1.id, job_id=jobs[6].id, action=SwipeAction.SKIP))

    if seeker2 and len(jobs) > 4:
        db.add(Swipe(user_id=seeker2.id, job_id=jobs[4].id, action=SwipeAction.APPLY))
        db.add(Swipe(user_id=seeker2.id, job_id=jobs[1].id, action=SwipeAction.SAVE))

    db.commit()


def main():
    print("Initializing database schema (create_all)...")
    init_db()

    db = SessionLocal()
    try:
        print("Seeding users...")
        users = seed_users(db)
        print(f"  -> {len(users)} users ready")

        print("Seeding companies...")
        companies = seed_companies(db, users)
        print(f"  -> {len(companies)} companies ready")

        print("Seeding jobs...")
        jobs = seed_jobs(db, companies, users)
        print(f"  -> {len(jobs)} jobs ready")

        print("Seeding swipes...")
        seed_swipes(db, users, jobs)
        print("  -> swipes ready")

        print("\nSeed complete! Test accounts (all use password: '%s'):" % TEST_PASSWORD)
        for email in users:
            print(f"  - {email}  (role: {users[email].role.value})")

    finally:
        db.close()


if __name__ == "__main__":
    main()
