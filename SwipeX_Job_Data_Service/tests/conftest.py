import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.core.database import Base, get_db
import app.models  # Crucial: Ensures Company, Job, Swipe tables register with Base.metadata
from app.core.cache import cache_manager
from app.main import app
from app.scripts.seed_data import seed_database

# Use an isolated in-memory SQLite database with StaticPool for test session persistence
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Sets up the test database schema and seeds it once for the test session."""
    Base.metadata.drop_all(bind=engine_test)
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    seed_database(db)
    db.close()
    yield
    Base.metadata.drop_all(bind=engine_test)


@pytest.fixture
def db_session():
    """Provides a fresh database session per test."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client(db_session):
    """Provides a FastAPI TestClient overriding the get_db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    # Clear cache between tests to prevent cross-test contamination
    cache_manager.clear()
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
