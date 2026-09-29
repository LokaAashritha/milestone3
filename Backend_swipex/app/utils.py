"""
app/utils.py

Small shared utility helpers used across controllers. Keeping these in one
place avoids duplicating the "dynamic job intelligence" calculations in both
the job controller and the recommendation controller.
"""

from datetime import datetime, timezone

from app.models import Job
from app.schemas import JobOut


def humanize_timedelta(dt: datetime) -> str:
    """
    Converts a datetime into a relative human-readable string,
    e.g. "just now", "5 minutes ago", "2 days ago", "3 months ago".
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    now = datetime.now(timezone.utc)
    delta = now - dt
    seconds = int(delta.total_seconds())

    if seconds < 0:
        seconds = 0

    if seconds < 60:
        return "just now"

    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"

    hours = minutes // 60
    if hours < 24:
        return f"{hours} hour{'s' if hours != 1 else ''} ago"

    days = hours // 24
    if days < 7:
        return f"{days} day{'s' if days != 1 else ''} ago"

    weeks = days // 7
    if days < 30:
        return f"{weeks} week{'s' if weeks != 1 else ''} ago"

    months = days // 30
    if days < 365:
        return f"{months} month{'s' if months != 1 else ''} ago"

    years = days // 365
    return f"{years} year{'s' if years != 1 else ''} ago"


def compute_competition_level(applicant_count: int) -> str:
    """
    Buckets applicant_count into a qualitative competition level:
        < 10        -> Low
        10 - 50     -> Medium
        > 50        -> High
    """
    if applicant_count is None:
        applicant_count = 0
    if applicant_count < 10:
        return "Low"
    if applicant_count <= 50:
        return "Medium"
    return "High"


def serialize_job(job: Job) -> JobOut:
    """
    Converts a Job ORM instance into a JobOut schema, attaching the two
    dynamically computed intelligence fields: posted_time and competition_level.
    """
    return JobOut(
        id=job.id,
        company_id=job.company_id,
        company_name=job.company.name if job.company is not None else None,
        title=job.title,
        description=job.description,
        location=job.location,
        job_type=job.job_type,
        experience_level=job.experience_level,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        skills_required=job.skills_required or [],
        fresher_friendly=bool(job.fresher_friendly),
        low_competition=bool(job.low_competition),
        applicant_count=job.applicant_count,
        is_active=bool(job.is_active),
        posted_at=job.posted_at,
        created_at=job.created_at,
        posted_time=humanize_timedelta(job.posted_at),
        competition_level=compute_competition_level(job.applicant_count),
    )
