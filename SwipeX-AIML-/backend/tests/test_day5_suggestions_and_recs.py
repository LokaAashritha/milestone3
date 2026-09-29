from backend.app.models.schemas import JobDetail, ResumeRecord
from backend.app.services.ai_suggestions import ai_suggestions_engine
from backend.app.services.recommendation_engine import recommendation_engine
from backend.app.services.resume_parser import resume_repo


def test_day5_ai_suggestions_generation():
    resume = ResumeRecord(
        resume_id="res_day5_alex",
        user_id="user_day5_alex",
        original_filename="alex_resume.pdf",
        file_path="/tmp/alex.pdf",
        file_type=".pdf",
        raw_text="Experienced Software Engineer. Proficient in Python, FastAPI, PostgreSQL.",
        parsed_skills=["Python", "FastAPI", "PostgreSQL"],
    )
    resume_repo.save(resume)

    job = JobDetail(
        job_id="job_day5_senior_py",
        title="Senior Python Architect",
        company="Big Tech",
        description="Looking for Python Architect with Docker, Kubernetes, AWS, and Microservices experience.",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Microservices"],
    )

    suggestions, missing_skills, missing_keywords = ai_suggestions_engine.generate_suggestions(resume, job)

    assert len(suggestions) > 0
    assert "Docker" in missing_skills or "Kubernetes" in missing_skills
    assert any("Gap" in s or "Boost" in s or "Structuring" in s for s in suggestions)


def test_day5_upgraded_recommendations_with_reason_tags():
    resume = ResumeRecord(
        resume_id="res_day5_rec",
        user_id="user_day5_rec",
        original_filename="react_dev.txt",
        file_path="/tmp/react_dev.txt",
        file_type=".txt",
        raw_text="Frontend Developer skilled in React, TypeScript, Tailwind CSS, Redux, and Next.js.",
        parsed_skills=["React", "TypeScript", "Tailwind CSS", "Redux", "Next.js"],
    )
    resume_repo.save(resume)

    recs = recommendation_engine.get_recommendations_for_user("user_day5_rec", limit=10)

    assert len(recs) > 0
    top_rec = recs[0]
    assert top_rec.match_percentage > 0.0
    assert isinstance(top_rec.reason_tags, list)
    assert len(top_rec.reason_tags) > 0
