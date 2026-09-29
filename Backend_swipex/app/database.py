"""
app/database.py

Sets up the SQLAlchemy engine, session factory, and declarative Base used
throughout the application. Also exposes the `get_db` FastAPI dependency
used by every controller to obtain a scoped database session.
"""

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Load environment variables from a .env file if present.
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/job_swipe_db",
)

# `pool_pre_ping` guards against stale connections being handed out after
# the database restarts or an idle connection is dropped by a proxy/firewall.
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    future=True,
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency that yields a database session and guarantees
    it is closed after the request finishes, even if an exception occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Creates all tables registered on `Base.metadata` if they do not already
    exist. Safe to call multiple times. Intended for local/dev bootstrap;
    production deployments should prefer a proper migration tool (e.g. Alembic),
    but this keeps the project runnable out-of-the-box without extra tooling.
    """
    # Import models here (not at module top) to avoid circular imports while
    # still ensuring all model classes are registered on Base.metadata
    # before create_all() is invoked.
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
