from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_swipe_recording_and_feedback_loop(sample_pdf_backend):
    # 1. Upload resume
    with open(sample_pdf_backend, "rb") as f:
        response = client.post(
            "/api/v1/resume/upload",
            files={"file": ("alex_resume.pdf", f, "application/pdf")},
            data={"user_id": "user_swipe_test"},
        )
    assert response.status_code == 201

    # 2. Get initial recommendations
    rec_res = client.get("/api/v1/recommendations?user_id=user_swipe_test")
    assert rec_res.status_code == 200
    initial_recs = rec_res.json()
    assert len(initial_recs) > 0
    top_job_id = initial_recs[0]["job_id"]

    # 3. Swipe 'skip' on top job
    swipe_res = client.post(
        "/api/v1/swipe",
        json={"user_id": "user_swipe_test", "job_id": top_job_id, "action": "skip"},
    )
    assert swipe_res.status_code == 201
    assert swipe_res.json()["status"] == "success"

    # 4. Get updated recommendations -> top_job_id must be excluded
    updated_rec_res = client.get("/api/v1/recommendations?user_id=user_swipe_test")
    assert updated_rec_res.status_code == 200
    updated_recs = updated_rec_res.json()
    updated_job_ids = [item["job_id"] for item in updated_recs]
    assert top_job_id not in updated_job_ids


def test_reason_tags_and_hybrid_scoring(sample_pdf_backend):
    # Upload resume
    with open(sample_pdf_backend, "rb") as f:
        client.post(
            "/api/v1/resume/upload",
            files={"file": ("alex_resume.pdf", f, "application/pdf")},
            data={"user_id": "user_reason_tags"},
        )

    # Heuristic feed
    res_h = client.get("/api/v1/recommendations?user_id=user_reason_tags")
    assert res_h.status_code == 200
    data_h = res_h.json()
    assert len(data_h) > 0
    assert "reason_tags" in data_h[0]
    assert isinstance(data_h[0]["reason_tags"], list)
    assert data_h[0]["generated_by"] in ["blended-v2", "heuristic-v0"]

    # Hybrid feed
    res_hybrid = client.get("/api/v1/recommendations?user_id=user_reason_tags&hybrid=true")
    assert res_hybrid.status_code == 200
    data_hybrid = res_hybrid.json()
    assert len(data_hybrid) > 0
    assert data_hybrid[0]["generated_by"] == "hybrid-v1"


def test_recommendation_match_breakdown(sample_pdf_backend):
    # Upload resume
    with open(sample_pdf_backend, "rb") as f:
        client.post(
            "/api/v1/resume/upload",
            files={"file": ("alex_resume.pdf", f, "application/pdf")},
            data={"user_id": "user_breakdown"},
        )

    # Get breakdown for job "1"
    res = client.get("/api/v1/recommendations/breakdown?job_id=1&user_id=user_breakdown")
    assert res.status_code == 200
    body = res.json()
    assert body["job_id"] == "1"
    assert "overall_match_percentage" in body
    assert "skill_overlap_percentage" in body
    assert "keyword_overlap_percentage" in body
    assert "semantic_similarity_percentage" in body
    assert isinstance(body["matched_skills"], list)
    assert isinstance(body["missing_skills"], list)
    assert "career_recommendation" in body


def test_career_intelligence_insights(sample_pdf_backend):
    # Upload resume
    with open(sample_pdf_backend, "rb") as f:
        client.post(
            "/api/v1/resume/upload",
            files={"file": ("alex_resume.pdf", f, "application/pdf")},
            data={"user_id": "user_career_intel"},
        )

    res = client.get("/api/v1/career-intelligence?user_id=user_career_intel")
    assert res.status_code == 200
    body = res.json()
    assert body["user_id"] == "user_career_intel"
    assert 0.0 <= body["readiness_score"] <= 100.0
    assert isinstance(body["top_missing_in_demand_skills"], list)
    assert isinstance(body["top_matched_skills"], list)
    assert "estimated_salary_fit" in body
    assert len(body["recommended_actions"]) > 0


def test_all_openapi_paths_registered():
    res = client.get("/api/v1/openapi.json")
    assert res.status_code == 200
    paths = res.json()["paths"]
    assert "/api/v1/resume/upload" in paths
    assert "/api/v1/resume/{resume_id}/ats-score" in paths
    assert "/api/v1/recommendations" in paths
    assert "/api/v1/recommendations/breakdown" in paths
    assert "/api/v1/swipe" in paths
    assert "/api/v1/career-intelligence" in paths
