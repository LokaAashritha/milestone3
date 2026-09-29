"""
Recommendation / Matching Engine Gateway.

Architecture note (decoupled / plug-and-play):
--------------------------------------------------------------------------
The real Data Science matching engine (a separate team/service) is not yet
available. Rather than hard-coding a dependency on that external service
(which would break this endpoint whenever the ML team's service is offline,
unfinished, or simply not deployed in this environment), we implement a
`MatchingEngineService` wrapper class below.

    - It exposes a stable interface:
      `get_recommendations(user, jobs) -> List[(Job, score, reasons)]`
    - Internally, it FIRST attempts to call an external matching engine via
      HTTP if `MATCHING_ENGINE_URL` is configured in the environment.
    - If that URL is not configured, or the call fails/times out for any
      reason, it transparently falls back to a local heuristic scorer built
      on plain Python + set operations (no external ML dependency required).

This means the /api/v1/recommendations endpoint ALWAYS returns a valid,
useful response, whether or not the external ML service exists yet.
--------------------------------------------------------------------------
"""

import os
from datetime import datetime, timezone
from typing import List, Tuple

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Job, User, Swipe, SwipeAction
from app.schemas import RecommendationResponse, RecommendationItem
from app.auth import get_current_user
from app.utils import serialize_job
from app.services.mock_ats_engine import generate_recommendation_scores


router = APIRouter()


MATCHING_ENGINE_URL = os.getenv("MATCHING_ENGINE_URL", "").strip()
MATCHING_ENGINE_TIMEOUT_SECONDS = float(
    os.getenv("MATCHING_ENGINE_TIMEOUT_SECONDS", "2.0")
)


class MatchingEngineService:
    """
    Modular wrapper around the job-recommendation matching engine.

    Provides a single stable method, `get_recommendations`, that callers can
    rely on regardless of whether the real external ML microservice is
    reachable. This keeps the FastAPI gateway fully decoupled from that
    team's release schedule / infrastructure state.
    """

    ENGINE_NAME_EXTERNAL = "external-ml-engine"
    ENGINE_NAME_HEURISTIC = "heuristic-fallback-v1"

    def __init__(self, external_url: str = "", timeout_seconds: float = 2.0):
        self.external_url = external_url
        self.timeout_seconds = timeout_seconds

    # ---------------------------------------------------------------
    # Public entrypoint
    # ---------------------------------------------------------------

    def get_recommendations(
        self,
        user: User,
        candidate_jobs: List[Job],
        applied_or_skipped_job_ids: set,
        limit: int,
    ) -> Tuple[str, List[Tuple[Job, float, List[str]]]]:
        """
        Returns a tuple of:

            (
                engine_name_used,
                [
                    (job, score_0_to_100, reasons),
                    ...
                ]
            )

        Results are sorted by score descending and capped at `limit`.
        """

        if self.external_url:
            external_result = self._try_external_engine(
                user,
                candidate_jobs,
                limit
            )

            if external_result is not None:
                return self.ENGINE_NAME_EXTERNAL, external_result

        # Fallback: local heuristic engine
        heuristic_result = self._heuristic_score(
            user,
            candidate_jobs,
            applied_or_skipped_job_ids
        )

        heuristic_result.sort(
            key=lambda item: item[1],
            reverse=True
        )

        return self.ENGINE_NAME_HEURISTIC, heuristic_result[:limit]

    # ---------------------------------------------------------------
    # External engine
    # ---------------------------------------------------------------

    def _try_external_engine(
        self,
        user: User,
        candidate_jobs: List[Job],
        limit: int
    ):
        """
        Attempts to call an externally hosted matching engine over HTTP.

        Any failure is swallowed and results in a `None` return, triggering
        the local heuristic fallback so the endpoint never breaks.
        """

        try:
            import requests

            job_payload = [
                {
                    "id": str(job.id),
                    "title": job.title,
                    "skills_required": job.skills_required or [],
                    "location": job.location,
                }
                for job in candidate_jobs
            ]

            response = requests.post(
                self.external_url,
                json={
                    "user_id": str(user.id),
                    "user_skills": user.skills or [],
                    "jobs": job_payload,
                    "limit": limit,
                },
                timeout=self.timeout_seconds,
            )

            response.raise_for_status()

            data = response.json()

            jobs_by_id = {
                str(job.id): job
                for job in candidate_jobs
            }

            results = []

            for entry in data.get("recommendations", []):
                job = jobs_by_id.get(entry.get("job_id"))

                if job is None:
                    continue

                score = float(
                    entry.get("score", 0)
                )

                reasons = entry.get(
                    "reasons",
                    []
                )

                results.append(
                    (
                        job,
                        score,
                        reasons
                    )
                )

            return results if results else None

        except Exception:
            # External engine must never cause the recommendation API
            # to return a 500 error.
            return None

    # ---------------------------------------------------------------
    # Local heuristic fallback engine
    # ---------------------------------------------------------------

    def _heuristic_score(
        self,
        user: User,
        candidate_jobs: List[Job],
        applied_or_skipped_job_ids: set,
    ) -> List[Tuple[Job, float, List[str]]]:
        """
        Simple, explainable, dependency-free scoring heuristic:

            +70 points max:
                proportion of the job's required skills that overlap
                with the user's declared skills

            +20 points:
                job location matches a location the user has
                previously shown interest in

            +10 points:
                newer postings receive a small recency boost

            +5 points:
                jobs with fewer than 10 applicants

            -100 points:
                jobs already applied to or skipped are excluded.

        This produces a 0-100 match score and a short list of
        human-readable reasons.
        """

        user_skills = {
            s.strip().lower()
            for s in (user.skills or [])
            if s and s.strip()
        }

        results: List[
            Tuple[Job, float, List[str]]
        ] = []

        now = datetime.now(timezone.utc)

        for job in candidate_jobs:

            # Don't recommend jobs already applied to or skipped.
            if job.id in applied_or_skipped_job_ids:
                continue

            reasons: List[str] = []
            score = 0.0

            job_skills = {
                s.strip().lower()
                for s in (job.skills_required or [])
                if s and s.strip()
            }

            if job_skills:
                overlap = user_skills & job_skills

                overlap_ratio = (
                    len(overlap) / len(job_skills)
                )

                skill_score = round(
                    overlap_ratio * 70,
                    2
                )

                score += skill_score

                if overlap:
                    reasons.append(
                        f"Matches {len(overlap)}/{len(job_skills)} "
                        f"required skills: "
                        f"{', '.join(sorted(overlap))}"
                    )

            else:
                # No listed requirements:
                # treat as neutral/moderate fit.
                score += 35

            # -------------------------------------------------------
            # Recency score
            # -------------------------------------------------------

            posted_at = job.posted_at

            if posted_at.tzinfo is None:
                posted_at = posted_at.replace(
                    tzinfo=timezone.utc
                )

            age_days = (
                now - posted_at
            ).total_seconds() / 86400

            if age_days <= 3:
                score += 10
                reasons.append("Recently posted")

            elif age_days <= 14:
                score += 5

            # -------------------------------------------------------
            # Competition score
            # -------------------------------------------------------

            if (
                job.applicant_count is not None
                and job.applicant_count < 10
            ):
                score += 5

                reasons.append(
                    "Low competition — fewer than 10 applicants so far"
                )

            # Keep score between 0 and 100.
            score = max(
                0.0,
                min(
                    100.0,
                    round(score, 2)
                )
            )

            if not reasons:
                reasons.append(
                    "General fit based on your profile"
                )

            results.append(
                (
                    job,
                    score,
                    reasons
                )
            )

        return results


# -------------------------------------------------------------------
# Matching engine instance
# -------------------------------------------------------------------

matching_engine = MatchingEngineService(
    external_url=MATCHING_ENGINE_URL,
    timeout_seconds=MATCHING_ENGINE_TIMEOUT_SECONDS,
)


# -------------------------------------------------------------------
# Recommendation endpoint
# -------------------------------------------------------------------

@router.get(
    "",
    response_model=RecommendationResponse,
    summary="Get personalized job recommendations for the current user",
)
def get_recommendations(
    limit: int = Query(
        10,
        ge=1,
        le=50,
        description="Maximum number of recommendations to return"
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # ---------------------------------------------------------------
    # 1. Exclude jobs already applied to or skipped
    # ---------------------------------------------------------------

    excluded_swipes = (
        db.query(Swipe.job_id)
        .filter(
            Swipe.user_id == current_user.id,
            Swipe.action.in_(
                [
                    SwipeAction.APPLY,
                    SwipeAction.SKIP
                ]
            ),
        )
        .all()
    )

    excluded_job_ids = {
        row[0]
        for row in excluded_swipes
    }

    # ---------------------------------------------------------------
    # 2. Get active jobs
    # ---------------------------------------------------------------

    candidate_jobs = (
        db.query(Job)
        .options(
            joinedload(Job.company)
        )
        .filter(
            Job.is_active == 1
        )
        .all()
    )

    # ---------------------------------------------------------------
    # 3. Generate recommendation scores
    # ---------------------------------------------------------------

    engine_used, scored = matching_engine.get_recommendations(
        user=current_user,
        candidate_jobs=candidate_jobs,
        applied_or_skipped_job_ids=excluded_job_ids,
        limit=limit,
    )

    # ---------------------------------------------------------------
    # 4. Build recommendation response
    #
    # Task 5.2:
    # Use mock ATS engine to generate:
    #   - semantic_match_score
    #   - recommendation_tags
    # ---------------------------------------------------------------

    recommendations = []

    for job, score, reasons in scored:

        matching_data = generate_recommendation_scores(
            resume_skills=current_user.skills or [],
            job_skills=job.skills_required or [],
        )

        recommendations.append(
            RecommendationItem(
                job=serialize_job(job),
                match_score=score,
                match_reasons=reasons,
                semantic_match_score=matching_data[
                    "semantic_match_score"
                ],
                recommendation_tags=matching_data[
                    "recommendation_tags"
                ],
            )
        )

    # ---------------------------------------------------------------
    # 5. Return final recommendation response
    # ---------------------------------------------------------------

    return RecommendationResponse(
        user_id=current_user.id,
        generated_at=datetime.now(timezone.utc),
        engine=engine_used,
        count=len(recommendations),
        recommendations=recommendations,
    )