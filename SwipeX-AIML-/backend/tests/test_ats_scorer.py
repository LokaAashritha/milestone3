import pytest
from fastapi import HTTPException

from backend.app.models.schemas import JobDetail, ResumeRecord
from backend.app.services.ats_scorer import ats_scoring_engine
from backend.app.services.resume_parser import resume_repo


def test_perfect_skill_match_score():
    resume = ResumeRecord(
        resume_id="res_test_1",
        original_filename="test.txt",
        file_path="/tmp/test.txt",
        file_type=".txt",
        raw_text="Experienced Senior Python Engineer with FastAPI, PostgreSQL, Docker, Redis.",
        parsed_skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
    )
    job = JobDetail(
        job_id="job_test_1",
        title="Python Engineer",
        company="TechCorp",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Redis"],
        description="Looking for Python Engineer with FastAPI, PostgreSQL, Docker and Redis experience.",
    )
    score, missing = ats_scoring_engine.calculate_score(resume, job)
    assert score >= 80.0
    assert missing == []


def test_partial_match_and_missing_keywords():
    resume = ResumeRecord(
        resume_id="res_test_2",
        original_filename="frontend.txt",
        file_path="/tmp/frontend.txt",
        file_type=".txt",
        raw_text="Frontend React developer working with JavaScript and CSS.",
        parsed_skills=["React", "JavaScript", "CSS3"],
    )
    job = JobDetail(
        job_id="job_test_2",
        title="Senior Python Backend Engineer",
        company="CloudCorp",
        skills=["Python", "FastAPI", "Docker", "Kubernetes", "PostgreSQL"],
        description="We need a Python FastAPI specialist who knows Docker and Kubernetes.",
    )
    score, missing = ats_scoring_engine.calculate_score(resume, job)
    assert score < 30.0
    assert "Python" in missing
    assert "FastAPI" in missing
    assert "Docker" in missing
    assert "Kubernetes" in missing


def test_detailed_keyword_score_and_threshold_detection():
    resume = ResumeRecord(
        resume_id="res_test_3",
        original_filename="partial.txt",
        file_path="/tmp/partial.txt",
        file_type=".txt",
        raw_text="Python developer working on REST APIs and Git.",
        parsed_skills=["Python", "REST API", "Git"],
    )
    job = JobDetail(
        job_id="job_test_3",
        title="Senior Python Developer",
        company="ScaleCorp",
        skills=["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"],
        description="Build scalable microservices with Python, FastAPI, PostgreSQL, Docker, and Kubernetes.",
    )
    score, missing_skills, missing_keywords = (
        ats_scoring_engine.calculate_detailed_keyword_score(resume, job)
    )
    assert score < 80.0
    assert "FastAPI" in missing_skills
    assert "Kubernetes" in missing_skills
    assert len(missing_keywords) > 0


def test_get_ats_score_not_found():
    with pytest.raises(HTTPException) as exc_info:
        ats_scoring_engine.get_ats_score(resume_id="non_existent_id", job_id="job_py_01")
    assert exc_info.value.status_code == 404

    dummy = ResumeRecord(
        resume_id="res_dummy",
        original_filename="dummy.txt",
        file_path="/tmp/dummy.txt",
        file_type=".txt",
        raw_text="Some text",
        parsed_skills=["Python"],
    )
    resume_repo.save(dummy)
    with pytest.raises(HTTPException) as exc_info2:
        ats_scoring_engine.get_ats_score(resume_id="res_dummy", job_id="non_existent_job_999")
    assert exc_info2.value.status_code == 404
