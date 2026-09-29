import pytest
from fastapi import HTTPException

from backend.app.models.schemas import JobDetail, ResumeRecord
from backend.app.services.ai_suggestions import ai_suggestions_engine
from backend.app.services.resume_parser import resume_repo


def test_ai_suggestions_generation():
    resume = ResumeRecord(
        resume_id="res_sugg_1",
        original_filename="alex.pdf",
        file_path="/tmp/alex.pdf",
        file_type=".pdf",
        raw_text="Python developer working with FastAPI and PostgreSQL.",
        parsed_skills=["Python", "FastAPI", "PostgreSQL"],
    )
    job = JobDetail(
        job_id="job_sugg_1",
        title="Senior Python Backend Developer",
        company="TechCorp",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        description="Looking for Python FastAPI developer with Docker and Kubernetes experience.",
    )
    suggestions, missing_skills, missing_keywords = ai_suggestions_engine.generate_suggestions(
        resume, job
    )
    assert len(suggestions) > 0
    assert "Docker" in missing_skills
    assert "Kubernetes" in missing_skills


def test_get_suggestions_for_resume_api():
    resume = ResumeRecord(
        resume_id="res_sugg_2",
        original_filename="sarah.txt",
        file_path="/tmp/sarah.txt",
        file_type=".txt",
        raw_text="Frontend React developer.",
        parsed_skills=["React"],
    )
    resume_repo.save(resume)

    res = ai_suggestions_engine.get_suggestions_for_resume("res_sugg_2", "1")
    assert res.resume_id == "res_sugg_2"
    assert res.target_threshold == 80.0
    assert len(res.suggestions) > 0


def test_get_suggestions_not_found():
    with pytest.raises(HTTPException) as exc_info:
        ai_suggestions_engine.get_suggestions_for_resume("non_existent_id", "1")
    assert exc_info.value.status_code == 404
