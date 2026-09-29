from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_m2_m3_full_integration():
    # Health check
    h = client.get("/health")
    assert h.status_code == 200
    assert h.json()["status"] == "healthy"

    # Swipe post validation
    err_swipe = client.post("/api/v1/swipe", json={"user_id": "u1", "job_id": "1", "action": "invalid_action"})
    assert err_swipe.status_code == 422

    # Anonymous career intelligence
    ci = client.get("/api/v1/career-intelligence")
    assert ci.status_code == 200
    assert ci.json()["user_id"] == "anonymous_user"
