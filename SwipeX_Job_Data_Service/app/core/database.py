from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings

# For SQLite, check_same_thread needs to be False for FastAPI multi-threaded requests
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def run_migrations():
    """
    Applies schema migrations for Milestone 3 (SRS Day 2 requirement).
    Ensures all tables (resumes, resume_skills, etc.) and new columns
    (required_skills, keywords on jobs) exist in the database.
    """
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            # Check SQLite table info for jobs
            result = conn.execute(text("PRAGMA table_info(jobs)"))
            cols = {row[1] for row in result.fetchall()}
            if "required_skills" not in cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN required_skills TEXT DEFAULT '[]'"))
            if "keywords" not in cols:
                conn.execute(text("ALTER TABLE jobs ADD COLUMN keywords TEXT DEFAULT '[]'"))
            conn.commit()
        except Exception as e:
            # If not SQLite or already up-to-date
            pass


def get_db():
    """Dependency generator for database sessions in FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
