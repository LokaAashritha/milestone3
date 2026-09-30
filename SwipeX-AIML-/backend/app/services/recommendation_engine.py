from backend.app.core.config import settings
from backend.app.models.schemas import (
    JobRecommendationItem,
    MatchBreakdownResponse,
    ResumeRecord,
)
from backend.app.services.ats_scorer import (
    ATSScoringEngine,
    ats_scoring_engine,
)
from backend.app.services.interaction_service import (
    InteractionService,
    interaction_service,
)
from backend.app.services.job_service_client import (
    JobServiceClient,
    job_service_client,
)
from backend.app.services.resume_parser import (
    ResumeRepository,
    resume_repo,
)
from backend.app.services.semantic_engine import (
    SemanticMatchingEngine,
    semantic_matching_engine,
)
from backend.app.services.skill_extractor import skill_extractor


class RecommendationEngine:
    """
    SwipeX Milestone 3 recommendation engine.

    Data ownership:
        - Jobs       -> Job Data Service
        - Resumes    -> Job Data Service
        - Swipes     -> Job Data Service
        - AI/ML      -> AIML Service

    The recommendation calculation remains inside AIML,
    while the underlying platform data comes from Job Data Service.
    """

    def __init__(
        self,
        resume_repository: ResumeRepository = resume_repo,
        job_client: JobServiceClient = job_service_client,
        scoring_engine: ATSScoringEngine = ats_scoring_engine,
        interactions: InteractionService = interaction_service,
        semantic_engine: SemanticMatchingEngine = semantic_matching_engine,
    ):
        self.repo = resume_repository
        self.job_client = job_client
        self.scoring_engine = scoring_engine
        self.interactions = interactions
        self.semantic_engine = semantic_engine

        self.generated_by = settings.GENERATED_BY_TAG

    # ------------------------------------------------------------------
    # Reason tags
    # ------------------------------------------------------------------

    def generate_reason_tags(
        self,
        resume: ResumeRecord,
        job,
        match_score: float,
        matched_skills: list[str],
    ) -> list[str]:
        tags: list[str] = []

        if match_score >= 75.0:
            tags.append(
                f"High match: {int(match_score)}% compatibility"
            )

        elif match_score >= 50.0:
            tags.append(
                f"Moderate match: {int(match_score)}% compatibility"
            )

        else:
            tags.append(
                f"Entry fit: {int(match_score)}% match score"
            )

        if matched_skills:
            top_skills = ", ".join(
                matched_skills[:2]
            )

            tags.append(
                f"Matches skills: {top_skills}"
            )

        if (
            job.remote
            or "remote" in job.location.lower()
        ):
            tags.append("Remote friendly")

        return tags

    # ------------------------------------------------------------------
    # Recommendations
    # ------------------------------------------------------------------

    def get_recommendations_for_user(
        self,
        user_id: str | None = None,
        limit: int = 50,
        workplace_type: str | None = None,
        hybrid: bool = False,
    ) -> list[JobRecommendationItem]:

        if not user_id:
            return []

        # --------------------------------------------------------------
        # 1. Get real resume from Job Data
        # --------------------------------------------------------------

        resume = self.repo.get_latest_by_user_id(
            user_id
        )

        if not resume:
            return []

        # --------------------------------------------------------------
        # 2. Get real jobs from Job Data
        # --------------------------------------------------------------

        all_jobs = self.job_client.list_jobs()

        if not all_jobs:
            return []

        # --------------------------------------------------------------
        # 3. Get real swipe history from Job Data
        # --------------------------------------------------------------

        skipped_ids = (
            self.interactions.get_user_skipped_job_ids(
                user_id
            )
        )

        liked_ids = (
            self.interactions.get_user_liked_job_ids(
                user_id
            )
        )

        # --------------------------------------------------------------
        # 4. Build skill preferences from positive interactions
        # --------------------------------------------------------------

        liked_skills: set[str] = set()

        for liked_job_id in liked_ids:
            liked_job = self.job_client.get_job(
                liked_job_id
            )

            if not liked_job:
                continue

            normalized_liked_skills = (
                skill_extractor.normalize_skills(
                    liked_job.skills
                )
            )

            liked_skills.update(
                normalized_liked_skills
            )

        # --------------------------------------------------------------
        # 5. Calculate recommendations
        # --------------------------------------------------------------

        recommendations: list[
            JobRecommendationItem
        ] = []

        engine_tag = (
            "hybrid-v1"
            if hybrid
            else self.generated_by
        )

        candidate_skills = set(
            skill_extractor.normalize_skills(
                resume.parsed_skills
            )
        )

        for job in all_jobs:

            # ----------------------------------------------------------
            # Exclude skipped jobs
            # ----------------------------------------------------------

            if str(job.job_id) in skipped_ids:
                continue

            # ----------------------------------------------------------
            # Workplace filtering
            # ----------------------------------------------------------

            if workplace_type:
                wp_clean = (
                    workplace_type
                    .lower()
                    .strip()
                )

                is_remote = (
                    job.remote
                    or "remote"
                    in job.location.lower()
                )

                if (
                    wp_clean == "remote"
                    and not is_remote
                ):
                    continue

                if (
                    wp_clean in ("on-site", "onsite")
                    and is_remote
                ):
                    continue

            # ----------------------------------------------------------
            # Calculate blended ATS/semantic score
            # ----------------------------------------------------------

            (
                blended_score,
                _keyword_score,
                semantic_score,
                _missing_skills,
                _missing_keywords,
            ) = (
                self.scoring_engine
                .calculate_detailed_blended_score(
                    resume,
                    job,
                )
            )

            # ----------------------------------------------------------
            # Exact matched skills
            # ----------------------------------------------------------

            normalized_job_skills = (
                skill_extractor.normalize_skills(
                    job.skills
                )
            )

            matched_skills = [
                skill
                for skill in normalized_job_skills
                if skill in candidate_skills
            ]

            # ----------------------------------------------------------
            # Optional hybrid semantic weighting
            # ----------------------------------------------------------

            if hybrid:
                final_score = round(
                    blended_score * 0.60
                    + semantic_score * 0.40,
                    1,
                )
            else:
                final_score = round(
                    blended_score,
                    1,
                )

            # ----------------------------------------------------------
            # Positive swipe feedback boost
            # ----------------------------------------------------------

            if liked_skills:
                has_liked_skill = any(
                    skill in liked_skills
                    for skill in normalized_job_skills
                )

                if has_liked_skill:
                    final_score = round(
                        min(
                            100.0,
                            final_score + 10.0,
                        ),
                        1,
                    )

            # ----------------------------------------------------------
            # Explain recommendation
            # ----------------------------------------------------------

            reason_tags = (
                self.generate_reason_tags(
                    resume,
                    job,
                    final_score,
                    matched_skills,
                )
            )

            recommendations.append(
                JobRecommendationItem(
                    job_id=str(job.job_id),
                    match_percentage=final_score,
                    generated_by=engine_tag,
                    reason_tags=reason_tags,
                )
            )

        # --------------------------------------------------------------
        # 6. Highest compatibility first
        # --------------------------------------------------------------

        recommendations.sort(
            key=lambda item: (
                -item.match_percentage,
                str(item.job_id),
            )
        )

        return recommendations[:limit]

    # ------------------------------------------------------------------
    # Match breakdown
    # ------------------------------------------------------------------

    def get_match_breakdown(
        self,
        user_id: str,
        job_id: str,
    ) -> MatchBreakdownResponse | None:

        resume = self.repo.get_latest_by_user_id(
            user_id
        )

        job = self.job_client.get_job(
            job_id
        )

        if not resume or not job:
            return None

        (
            blended_score,
            keyword_score,
            semantic_score,
            missing_skills,
            missing_keywords,
        ) = (
            self.scoring_engine
            .calculate_detailed_blended_score(
                resume,
                job,
            )
        )

        candidate_skills = set(
            skill_extractor.normalize_skills(
                resume.parsed_skills
            )
        )

        normalized_job_skills = (
            skill_extractor.normalize_skills(
                job.skills
            )
        )

        matched_skills = sorted(
            [
                skill
                for skill in normalized_job_skills
                if skill in candidate_skills
            ]
        )

        total_job_skills = max(
            1,
            len(normalized_job_skills),
        )

        skill_overlap_pct = round(
            (
                len(matched_skills)
                / total_job_skills
            )
            * 100.0,
            1,
        )

        keyword_overlap_pct = round(
            max(
                0.0,
                (
                    keyword_score
                    - skill_overlap_pct * 0.70
                )
                / 0.30,
            ),
            1,
        )

        overall_score = round(
            blended_score,
            1,
        )

        reason_tags = (
            self.generate_reason_tags(
                resume,
                job,
                overall_score,
                matched_skills,
            )
        )

        if missing_skills:
            recommendation = (
                "To reach 80%+ match score, "
                "acquire or highlight: "
                f"{', '.join(missing_skills[:3])}."
            )
        else:
            recommendation = (
                "Excellent match! Your skill set "
                "aligns directly with this job posting."
            )

        return MatchBreakdownResponse(
            job_id=str(job.job_id),
            job_title=job.title,
            company_name=job.company,
            overall_match_percentage=overall_score,
            skill_overlap_percentage=skill_overlap_pct,
            keyword_overlap_percentage=keyword_overlap_pct,
            semantic_similarity_percentage=semantic_score,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            reason_tags=reason_tags,
            career_recommendation=recommendation,
            generated_by=self.generated_by,
        )


recommendation_engine = RecommendationEngine()