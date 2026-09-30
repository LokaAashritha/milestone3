"""
app/database.py

Sets up the SQLAlchemy engine, session factory, declarative Base,
and lightweight development migrations for the SwipeX Gateway.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/job_swipe_db",
)


# ---------------------------------------------------------------------------
# Database engine
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# FastAPI database dependency
# ---------------------------------------------------------------------------

def get_db():
    """
    FastAPI dependency that yields a database session and guarantees
    that it is closed after the request finishes.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Database initialization + lightweight migrations
# ---------------------------------------------------------------------------

def init_db() -> None:
    """
    Creates missing tables and applies the small schema migrations required
    by the integrated SwipeX architecture.

    Gateway uses UUID IDs.
    Job Data uses INTEGER IDs.

    Therefore:
        companies.job_data_company_id
        jobs.job_data_id

    store the corresponding Job Data identifiers.

    For production, Alembic migrations are preferable. This lightweight
    migration keeps the local/intern execution process simple.
    """

    # Import models here so every model is registered with Base.metadata.
    from app import models  # noqa: F401

    # Create missing tables.
    Base.metadata.create_all(bind=engine)

    # Apply missing columns to existing tables.
    with engine.begin() as connection:

        # -------------------------------------------------------------------
        # Company → Job Data company mapping
        # -------------------------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE companies
                ADD COLUMN IF NOT EXISTS job_data_company_id INTEGER
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                ix_companies_job_data_company_id
                ON companies(job_data_company_id)
                """
            )
        )

        # -------------------------------------------------------------------
        # Job → Job Data job mapping
        # -------------------------------------------------------------------

        connection.execute(
            text(
                """
                ALTER TABLE jobs
                ADD COLUMN IF NOT EXISTS job_data_id INTEGER
                """
            )
        )

        connection.execute(
            text(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS
                ix_jobs_job_data_id
                ON jobs(job_data_id)
                """
            )
        )


# ---------------------------------------------------------------------------
# Optional explicit migration helper
# ---------------------------------------------------------------------------

def migrate_db() -> None:
    """
    Alias for init_db() so startup code can explicitly call the migration
    step if desired.
    """
    init_db()