import pytest
from fastapi.testclient import TestClient


def test_record_right_swipe_apply(client: TestClient):
    # Fetch a job first
    jobs_res = client.get("/api/v1/jobs")
    job_id = jobs_res.json()[0]["job_id"]

    swipe_payload = {
        "job_id": job_id,
        "direction": "right",
        "action_type": "apply",
        "user_id": "test-user-101"
    }

    response = client.post("/api/v1/swipes", json=swipe_payload)
    assert response.status_code == 201
    data = response.json()
    assert "swipe_id" in data
    assert data["direction"] == "right"
    assert data["action_type"] == "apply"
    assert data["job_id"] == job_id


def test_record_left_swipe_skip(client: TestClient):
    jobs_res = client.get("/api/v1/jobs")
    job_id = jobs_res.json()[1]["job_id"]

    swipe_payload = {
        "job_id": job_id,
        "direction": "left",
        "action_type": "skip",
        "user_id": "test-user-101"
    }

    response = client.post("/api/v1/swipes", json=swipe_payload)
    assert response.status_code == 201
    data = response.json()
    assert data["direction"] == "left"
    assert data["action_type"] == "skip"


def test_record_swipe_invalid_job(client: TestClient):
    swipe_payload = {
        "job_id": 999999,
        "direction": "right",
        "action_type": "apply",
        "user_id": "test-user-101"
    }
    response = client.post("/api/v1/swipes", json=swipe_payload)
    assert response.status_code == 404


def test_get_swipe_history(client: TestClient):
    # Retrieve swipe history for user 'test-user-101'
    response = client.get("/api/v1/swipes/history?user_id=test-user-101")
    assert response.status_code == 200
    history = response.json()
    assert isinstance(history, list)
    assert len(history) >= 2
    # Check SRS 7.2 contract
    first_item = history[0]
    assert "job_id" in first_item
    assert "direction" in first_item
    assert "swiped_at" in first_item


def test_get_swipe_summary(client: TestClient):
    response = client.get("/api/v1/swipes/summary?user_id=test-user-101")
    assert response.status_code == 200
    summary = response.json()
    assert summary["user_id"] == "test-user-101"
    assert summary["total_swipes"] >= 2
    assert summary["right_swipes"] >= 1
    assert summary["left_swipes"] >= 1
