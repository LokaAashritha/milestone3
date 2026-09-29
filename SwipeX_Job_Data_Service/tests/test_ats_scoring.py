import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.job import Job
from app.models.resume import Resume, ParsedStatus

client = TestClient(app)
TEST_USER_ID = "4f9c2e3d-1111-4444-8888-123456789abc"


def test_ats_scoring_high_match_empty_missing():
    """
    FR-04 Rule: When ATS match score >= 80%, missing_skills and missing_keywords
    MUST be returned as empty arrays [].
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.is_active == True).first()
        assert job is not None
        target_job_id = job.id

        # Create a resume with matching skills
        resume = Resume(
            user_id=TEST_USER_ID,
            file_name="high_match_resume.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="./uploads/resumes/high_match_resume.pdf",
            version_number=10,
            is_active_version=True,
            parsed_status=ParsedStatus.DONE.value,
            parsed_text="Experienced developer with " + " ".join(job.required_skills) + " " + " ".join(job.keywords)
        )
        resume.extracted_skills = job.required_skills + job.keywords
        db.add(resume)
        db.commit()
        db.refresh(resume)
        resume_id = resume.id
    finally:
        db.close()

    headers = {"x-user-id": TEST_USER_ID}
    payload = {
        "resume_id": resume_id,
        "job_id": target_job_id
    }

    response = client.post("/api/v1/ats/score", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["match_score"] >= 80.0
    # Rule FR-04: empty arrays when >= 80%
    assert data["missing_skills"] == []
    assert data["missing_keywords"] == []
    assert "scored_at" in data


def test_ats_scoring_low_match_populates_missing():
    """
    FR-04 Rule: When ATS match score < 80%, system identifies and returns
    missing_skills and missing_keywords.
    """
    db = SessionLocal()
    try:
        job = db.query(Job).filter(Job.is_active == True).first()
        assert job is not None
        target_job_id = job.id

        # Create a resume with minimal/unrelated skills
        resume = Resume(
            user_id=TEST_USER_ID,
            file_name="low_match_resume.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="./uploads/resumes/low_match_resume.pdf",
            version_number=11,
            is_active_version=False,
            parsed_status=ParsedStatus.DONE.value,
            parsed_text="Junior applicant with basic understanding of HTML and Excel."
        )
        resume.extracted_skills = ["HTML", "Excel"]
        db.add(resume)
        db.commit()
        db.refresh(resume)
        resume_id = resume.id
    finally:
        db.close()

    headers = {"x-user-id": TEST_USER_ID}
    payload = {
        "resume_id": resume_id,
        "job_id": target_job_id
    }

    response = client.post("/api/v1/ats/score", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["match_score"] < 80.0
    # Rule FR-04: populated when < 80%
    assert len(data["missing_skills"]) > 0
    assert "scored_at" in data


def test_ats_scoring_unparsed_resume_error():
    """Attempting to score an unparsed resume returns 400 Bad Request."""
    db = SessionLocal()
    try:
        resume = Resume(
            user_id=TEST_USER_ID,
            file_name="unparsed_resume.pdf",
            file_type="pdf",
            file_size=1024,
            file_path="./uploads/resumes/unparsed_resume.pdf",
            version_number=12,
            is_active_version=False,
            parsed_status=ParsedStatus.PENDING.value,
            parsed_text=None
        )
        resume.extracted_skills = []
        db.add(resume)
        db.commit()
        db.refresh(resume)
        resume_id = resume.id
    finally:
        db.close()

    headers = {"x-user-id": TEST_USER_ID}
    payload = {
        "resume_id": resume_id,
        "job_id": 1
    }

    response = client.post("/api/v1/ats/score", json=payload, headers=headers)
    assert response.status_code == 400
    assert "not yet parsed" in response.json()["detail"]


def test_ats_scoring_job_not_found():
    """Scoring against a non-existent job ID returns 404 Not Found."""
    headers = {"x-user-id": TEST_USER_ID}
    payload = {
        "resume_id": "b1a2c3d4-0000-4444-8888-abcdefabcdef",
        "job_id": 99999999
    }
    response = client.post("/api/v1/ats/score", json=payload, headers=headers)
    assert response.status_code == 404
