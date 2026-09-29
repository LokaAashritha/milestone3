from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.resume_parser import resume_repo


@pytest.fixture(autouse=True)
def reset_resume_repo():
    resume_repo.clear()
    yield
    resume_repo.clear()


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def sample_data_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "app" / "data" / "sample_resumes"


@pytest.fixture
def sample_pdf_backend(sample_data_dir) -> Path:
    return sample_data_dir / "resume_backend_alex.pdf"


@pytest.fixture
def sample_txt_frontend(sample_data_dir) -> Path:
    return sample_data_dir / "resume_frontend_sarah.txt"


@pytest.fixture
def sample_pdf_ml(sample_data_dir) -> Path:
    return sample_data_dir / "resume_ml_marcus.pdf"


@pytest.fixture
def sample_txt_junior(sample_data_dir) -> Path:
    return sample_data_dir / "resume_junior_jordan.txt"
