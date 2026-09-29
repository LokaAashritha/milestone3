from datetime import datetime, timezone
from typing import Dict, Any


def compute_job_freshness(posted_at: datetime) -> Dict[str, Any]:
    """
    Rule-based computation of job freshness indicators based on posted_time.
    Rules:
    - <= 1 day (24 hours): "Just Posted" (is_fresh = True)
    - <= 3 days: "Recently Posted" (is_fresh = True)
    - <= 7 days: "This Week" (is_fresh = True)
    - > 7 days: "Active" (is_fresh = False)
    """
    now = datetime.utcnow()
    # Normalize if timezone-aware
    if posted_at.tzinfo is not None:
        posted_at = posted_at.astimezone(timezone.utc).replace(tzinfo=None)

    diff = now - posted_at
    total_seconds = max(0, int(diff.total_seconds()))
    days_ago = total_seconds // 86400
    hours_ago = total_seconds // 3600

    if hours_ago < 24:
        label = "Just Posted"
        is_fresh = True
    elif days_ago <= 3:
        label = "Recently Posted"
        is_fresh = True
    elif days_ago <= 7:
        label = "This Week"
        is_fresh = True
    else:
        label = "Active"
        is_fresh = False

    return {
        "freshness_label": label,
        "days_ago": days_ago,
        "hours_ago": hours_ago,
        "is_fresh": is_fresh
    }


def compute_competition_level(applicant_count: int) -> Dict[str, Any]:
    """
    Rule-based computation of competition level from applicant count thresholds:
    - < 25 applicants: "Low" (Early opportunity)
    - 25 - 100 applicants: "Medium" (Balanced competition)
    - > 100 applicants: "High" (High competition)

    Early applicant indicator:
    - < 15 applicants: is_early_applicant = True
    """
    count = max(0, applicant_count)

    if count < 25:
        level = "Low"
    elif count <= 100:
        level = "Medium"
    else:
        level = "High"

    is_early_applicant = count < 15
    # Calculate a normalized competition score (0 to 100)
    score = min(100.0, round((count / 150.0) * 100.0, 1))

    return {
        "competition_level": level,
        "applicant_count": count,
        "is_early_applicant": is_early_applicant,
        "competition_score": score
    }
