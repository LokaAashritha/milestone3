from datetime import datetime, timedelta
from app.core.intelligence import compute_job_freshness, compute_competition_level


def test_freshness_just_posted():
    posted = datetime.utcnow() - timedelta(hours=4)
    info = compute_job_freshness(posted)
    assert info["freshness_label"] == "Just Posted"
    assert info["is_fresh"] is True


def test_freshness_recently_posted():
    posted = datetime.utcnow() - timedelta(days=2)
    info = compute_job_freshness(posted)
    assert info["freshness_label"] == "Recently Posted"
    assert info["is_fresh"] is True


def test_freshness_active():
    posted = datetime.utcnow() - timedelta(days=12)
    info = compute_job_freshness(posted)
    assert info["freshness_label"] == "Active"
    assert info["is_fresh"] is False


def test_competition_low_early():
    info = compute_competition_level(12)
    assert info["competition_level"] == "Low"
    assert info["is_early_applicant"] is True


def test_competition_medium():
    info = compute_competition_level(45)
    assert info["competition_level"] == "Medium"
    assert info["is_early_applicant"] is False


def test_competition_high():
    info = compute_competition_level(150)
    assert info["competition_level"] == "High"
    assert info["is_early_applicant"] is False
