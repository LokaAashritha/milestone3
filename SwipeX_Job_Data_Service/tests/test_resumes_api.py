import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.resume_service import ResumeService
from app.core.database import SessionLocal
from app.models.resume import Resume

client = TestClient(app)
TEST_USER_ID = "4f9c2e3d-1111-4444-8888-123456789abc"


def test_upload_resume_pdf_success():
    """Valid PDF resume upload creates a new active version row (FR-01, contract 201)."""
    fake_pdf_content = b"%PDF-1.4 Mock PDF Content with Python, FastAPI, and Docker skills..."
    files = {"file": ("test_resume.pdf", io.BytesIO(fake_pdf_content), "application/pdf")}
    data = {"user_id": TEST_USER_ID, "is_active_version": "true"}

    response = client.post("/api/v1/resumes/upload", files=files, data=data)
    assert response.status_code == 201
    payload = response.json()
    assert payload["file_name"] == "test_resume.pdf"
    assert payload["file_type"] == "pdf"
    assert payload["user_id"] == TEST_USER_ID
    assert payload["is_active_version"] is True
    assert payload["parsed_status"] == "pending"
    assert "id" in payload


def test_upload_resume_docx_success():
    """Valid DOCX resume upload succeeds."""
    fake_docx = b"PK\x03\x04 Mock DOCX Content for Senior Developer..."
    files = {"file": ("portfolio_resume.docx", io.BytesIO(fake_docx), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    data = {"user_id": TEST_USER_ID, "is_active_version": "true"}

    response = client.post("/api/v1/resumes/upload", files=files, data=data)
    assert response.status_code == 201
    payload = response.json()
    assert payload["file_name"] == "portfolio_resume.docx"
    assert payload["file_type"] == "docx"


def test_upload_resume_invalid_format():
    """Unsupported format returns 400 Bad Request."""
    fake_txt = b"Text file contents..."
    files = {"file": ("invalid_resume.txt", io.BytesIO(fake_txt), "text/plain")}
    data = {"user_id": TEST_USER_ID}

    response = client.post("/api/v1/resumes/upload", files=files, data=data)
    assert response.status_code == 400
    assert "Only PDF and DOCX" in response.json()["detail"]


def test_upload_resume_exceeds_size_limit():
    """Files exceeding 10MB limit return 413 Request Entity Too Large."""
    # 10.5 MB payload
    large_payload = b"0" * (11 * 1024 * 1024)
    files = {"file": ("huge_resume.pdf", io.BytesIO(large_payload), "application/pdf")}
    data = {"user_id": TEST_USER_ID}

    response = client.post("/api/v1/resumes/upload", files=files, data=data)
    assert response.status_code == 413
    assert "exceeds maximum limit of 10MB" in response.json()["detail"]


def test_list_resumes():
    """GET /api/v1/resumes returns user's versions newest first."""
    headers = {"x-user-id": TEST_USER_ID}
    response = client.get("/api/v1/resumes", headers=headers)
    assert response.status_code == 200
    versions = response.json()
    assert isinstance(versions, list)
    assert len(versions) >= 1
    for r in versions:
        assert r["user_id"] == TEST_USER_ID


def test_list_resumes_active_only():
    """GET /api/v1/resumes?active_only=true returns only the current active version."""
    headers = {"x-user-id": TEST_USER_ID}
    response = client.get("/api/v1/resumes?active_only=true", headers=headers)
    assert response.status_code == 200
    versions = response.json()
    for r in versions:
        assert r["is_active_version"] is True


def test_get_resume_detail():
    """GET /api/v1/resumes/{id} returns full metadata."""
    headers = {"x-user-id": TEST_USER_ID}
    list_res = client.get("/api/v1/resumes", headers=headers)
    resume_id = list_res.json()[0]["id"]

    response = client.get(f"/api/v1/resumes/{resume_id}", headers=headers)
    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == resume_id
    assert "file_size" in detail


def test_get_resume_not_found():
    """GET /api/v1/resumes/{id} returns 404 for non-existent resume."""
    headers = {"x-user-id": TEST_USER_ID}
    response = client.get("/api/v1/resumes/non-existent-uuid-1234", headers=headers)
    assert response.status_code == 404


def test_trigger_resume_parse():
    """POST /api/v1/resumes/{id}/parse updates status to done and stores skills."""
    headers = {"x-user-id": TEST_USER_ID}
    # Upload fresh resume
    fake_pdf = b"%PDF-1.4 Clean engineer resume content..."
    files = {"file": ("engineer_resume.pdf", io.BytesIO(fake_pdf), "application/pdf")}
    upload_res = client.post("/api/v1/resumes/upload", files=files, data={"user_id": TEST_USER_ID})
    resume_id = upload_res.json()["id"]

    # Trigger parse
    parse_payload = {
        "parsed_text": "Experienced Python Backend Engineer specializing in FastAPI, PostgreSQL, and Docker.",
        "extracted_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "REST APIs"]
    }
    parse_res = client.post(f"/api/v1/resumes/{resume_id}/parse", json=parse_payload, headers=headers)
    assert parse_res.status_code == 200
    data = parse_res.json()
    assert data["parsed_status"] == "done"
    assert "FastAPI" in data["extracted_skills"]
    assert "Python" in data["extracted_skills"]


def test_activate_resume_version():
    """PATCH /api/v1/resumes/{id}/activate sets specified version active."""
    headers = {"x-user-id": TEST_USER_ID}
    list_res = client.get("/api/v1/resumes", headers=headers)
    resumes = list_res.json()
    target_id = resumes[-1]["id"]

    activate_res = client.patch(f"/api/v1/resumes/{target_id}/activate", headers=headers)
    assert activate_res.status_code == 200
    assert activate_res.json()["is_active_version"] is True
