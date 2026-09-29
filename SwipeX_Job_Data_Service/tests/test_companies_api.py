import pytest
from fastapi.testclient import TestClient


def test_get_companies_list(client: TestClient):
    response = client.get("/api/v1/companies")
    assert response.status_code == 200
    companies = response.json()
    assert isinstance(companies, list)
    assert len(companies) > 0
    first = companies[0]
    assert "id" in first
    assert "name" in first
    assert "company_type" in first
    assert "industry" in first


def test_get_companies_filter_newly_founded(client: TestClient):
    response = client.get("/api/v1/companies?newly_founded=true")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) > 0
    for c in companies:
        assert c["is_newly_founded"] is True


def test_get_companies_search(client: TestClient):
    response = client.get("/api/v1/companies?search=Google")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) == 1
    assert companies[0]["name"] == "Google"


def test_get_company_detail_with_jobs(client: TestClient):
    # Fetch first company
    list_res = client.get("/api/v1/companies")
    company_id = list_res.json()[0]["id"]

    response = client.get(f"/api/v1/companies/{company_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == company_id
    assert "active_jobs_count" in data
    assert "jobs" in data
    assert isinstance(data["jobs"], list)


def test_get_company_not_found(client: TestClient):
    response = client.get("/api/v1/companies/999999")
    assert response.status_code == 404
