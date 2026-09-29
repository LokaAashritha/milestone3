from fastapi.testclient import TestClient

from src.main import app
from src.parser import resume_repo

client = TestClient(app)


def test_day2_matching_engine_skeleton():
    resume_repo.clear()

    resp_empty = client.get("/api/v1/recommendations?user_id=new_user_no_resume")
    assert resp_empty.status_code == 200
    assert resp_empty.json() == []

    txt_content = b"Alex Rivera\nSenior Backend Engineer\nSkills: Python, FastAPI, PostgreSQL, Docker, Redis."
    files = {"file": ("alex_resume.txt", txt_content, "text/plain")}
    data = {"user_id": "user_alex_day2"}

    upload_resp = client.post("/api/v1/resume/upload", files=files, data=data)
    assert upload_resp.status_code == 201

    rec_resp = client.get("/api/v1/recommendations?user_id=user_alex_day2")
    assert rec_resp.status_code == 200
    recs = rec_resp.json()
    assert len(recs) > 0
    assert "job_id" in recs[0]
    assert "match_percentage" in recs[0]
    assert recs[0]["generated_by"] == "heuristic-v0"
    assert recs[0]["match_percentage"] > 0
