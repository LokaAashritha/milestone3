from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["mode"] in ["blended-v2", "heuristic-v0"]


def test_resume_upload_pdf(client: TestClient, sample_pdf_backend):
    with open(sample_pdf_backend, "rb") as f:
        files = {"file": ("alex_resume.pdf", f, "application/pdf")}
        data = {"user_id": "user_alex_101"}
        response = client.post("/api/v1/resume/upload", files=files, data=data)

    assert response.status_code == 201
    res_data = response.json()
    assert "resume_id" in res_data
    assert res_data["resume_id"].startswith("res_")
    assert isinstance(res_data["parsed_skills"], list)
    assert "Python" in res_data["parsed_skills"]
    assert "FastAPI" in res_data["parsed_skills"]


def test_resume_upload_txt(client: TestClient, sample_txt_frontend):
    with open(sample_txt_frontend, "rb") as f:
        files = {"file": ("sarah_resume.txt", f, "text/plain")}
        data = {"user_id": "user_sarah_102"}
        response = client.post("/api/v1/resume/upload", files=files, data=data)

    assert response.status_code == 201
    res_data = response.json()
    assert "resume_id" in res_data
    assert "React" in res_data["parsed_skills"]
    assert "Tailwind CSS" in res_data["parsed_skills"]


def test_resume_upload_with_gateway_header(client: TestClient, sample_txt_junior):
    with open(sample_txt_junior, "rb") as f:
        files = {"file": ("jordan_resume.txt", f, "text/plain")}
        headers = {"X-User-ID": "user_jordan_103"}
        response = client.post("/api/v1/resume/upload", files=files, headers=headers)

    assert response.status_code == 201
    res_data = response.json()
    assert "resume_id" in res_data


def test_resume_upload_invalid_extension(client: TestClient):
    files = {"file": ("resume.exe", b"binary content", "application/octet-stream")}
    response = client.post("/api/v1/resume/upload", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_resume_upload_empty_file(client: TestClient):
    files = {"file": ("empty.txt", b"", "text/plain")}
    response = client.post("/api/v1/resume/upload", files=files)
    assert response.status_code == 400
    assert "empty" in response.json()["detail"].lower()


def test_ats_score_endpoint(client: TestClient, sample_pdf_backend):
    with open(sample_pdf_backend, "rb") as f:
        files = {"file": ("alex_resume.pdf", f, "application/pdf")}
        upload_resp = client.post("/api/v1/resume/upload", files=files)
    resume_id = upload_resp.json()["resume_id"]

    ats_resp = client.get(f"/api/v1/resume/{resume_id}/ats-score?job_id=5")
    assert ats_resp.status_code == 200
    ats_data = ats_resp.json()
    assert "match_score" in ats_data
    assert ats_data["match_score"] >= 30.0
    assert "missing_keywords" in ats_data
    assert isinstance(ats_data["missing_keywords"], list)
    assert ats_data["generated_by"] in ["blended-v2", "heuristic-v0"]


def test_ats_score_endpoint_not_found(client: TestClient):
    resp = client.get("/api/v1/resume/non_existent_id/ats-score?job_id=5")
    assert resp.status_code == 404


def test_recommendations_endpoint(client: TestClient, sample_pdf_backend):
    resp_empty = client.get("/api/v1/recommendations?user_id=new_user_without_resume")
    assert resp_empty.status_code == 200
    assert resp_empty.json() == []

    with open(sample_pdf_backend, "rb") as f:
        files = {"file": ("alex_resume.pdf", f, "application/pdf")}
        data = {"user_id": "user_alex_rec_test"}
        client.post("/api/v1/resume/upload", files=files, data=data)

    resp_recs = client.get("/api/v1/recommendations?user_id=user_alex_rec_test")
    assert resp_recs.status_code == 200
    recs = resp_recs.json()
    assert len(recs) > 0
    assert recs[0]["generated_by"] in ["blended-v2", "heuristic-v0"]
    assert "match_percentage" in recs[0]


def test_openapi_docs(client: TestClient):
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "paths" in schema
    assert "/api/v1/resume/upload" in schema["paths"]
    assert "/api/v1/resume/{resume_id}/ats-score" in schema["paths"]
    assert "/api/v1/recommendations" in schema["paths"]
