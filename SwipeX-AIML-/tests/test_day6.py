from fastapi.testclient import TestClient

from src.main import app
from src.parser import resume_repo

client = TestClient(app)


def test_day6_health_and_parsing():
    resume_repo.clear()

    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    txt_content = b"Alex Rivera\nSenior Backend Engineer\nSkills: Python, FastAPI, PostgreSQL, Docker."
    files = {"file": ("alex.txt", txt_content, "text/plain")}
    data = {"user_id": "user_alex_test"}

    upload_resp = client.post("/api/v1/resume/upload", files=files, data=data)
    assert upload_resp.status_code == 201
    upload_data = upload_resp.json()
    assert "resume_id" in upload_data
    assert "Python" in upload_data["parsed_skills"]
    assert "FastAPI" in upload_data["parsed_skills"]

    resume_id = upload_data["resume_id"]
    ats_resp = client.get(f"/api/v1/resume/{resume_id}/ats-score?job_id=5")
    assert ats_resp.status_code == 200
    assert ats_resp.json()["match_score"] > 0.0

    rec_resp = client.get("/api/v1/recommendations?user_id=user_alex_test")
    assert rec_resp.status_code == 200
    assert len(rec_resp.json()) > 0
