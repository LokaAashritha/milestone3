import pytest
from fastapi.testclient import TestClient


def test_save_job_success(client: TestClient):
    jobs_res = client.get("/api/v1/jobs")
    job_id = jobs_res.json()[0]["job_id"]

    payload = {
        "job_id": job_id,
        "notes": "Target role for frontend applications",
        "user_id": "test-user-m2"
    }

    response = client.post("/api/v1/saved-jobs", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["job_id"] == job_id
    assert data["user_id"] == "test-user-m2"
    assert "saved_at" in data


def test_get_saved_jobs(client: TestClient):
    response = client.get("/api/v1/saved-jobs?user_id=test-user-m2")
    assert response.status_code == 200
    items = response.json()
    assert isinstance(items, list)
    assert len(items) >= 1
    assert items[0]["user_id"] == "test-user-m2"
    assert "job" in items[0]
    assert items[0]["job"] is not None


def test_delete_saved_job(client: TestClient):
    # Save a job first
    jobs_res = client.get("/api/v1/jobs")
    job_id = jobs_res.json()[1]["job_id"]

    client.post("/api/v1/saved-jobs", json={"job_id": job_id, "user_id": "test-user-del"})

    # Delete it
    del_res = client.delete(f"/api/v1/saved-jobs/{job_id}?user_id=test-user-del")
    assert del_res.status_code == 200
    assert del_res.json()["status"] == "success"

    # Verify not in saved list
    check_res = client.get("/api/v1/saved-jobs?user_id=test-user-del")
    assert not any(item["job_id"] == job_id for item in check_res.json())
