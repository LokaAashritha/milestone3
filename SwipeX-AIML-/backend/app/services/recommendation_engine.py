from backend.app.core.config import settings
from backend.app.models.schemas import JobRecommendationItem, MatchBreakdownResponse, ResumeRecord
from backend.app.services.ats_scorer import ATSScoringEngine, ats_scoring_engine
from backend.app.services.interaction_service import InteractionService, interaction_service
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo
from backend.app.services.semantic_engine import SemanticMatchingEngine, semantic_matching_engine
from backend.app.services.skill_extractor import skill_extractor


class RecommendationEngine:
    """Milestone 3 Day 5: Upgraded Semantic & Swipe-Aware Recommendation Engine.

    Blends candidate resume vector embeddings with active job vectors and applies swipe-history
    feedback loops (like +15%, save +20%, skip exclude) to produce personalized job recommendations.
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

    def generate_reason_tags(
        self, resume: ResumeRecord, job, match_score: float, matched_skills: list[str]
    ) -> list[str]:
        tags: list[str] = []
        if match_score >= 75.0:
            tags.append(f"High match: {int(match_score)}% compatibility")
        elif match_score >= 50.0:
            tags.append(f"Moderate match: {int(match_score)}% compatibility")
        else:
            tags.append(f"Entry fit: {int(match_score)}% match score")

        if matched_skills:
            top_skills = ", ".join(matched_skills[:2])
            tags.append(f"Matches skills: {top_skills}")

        if job.remote or "remote" in job.location.lower():
            tags.append("Remote friendly")

        return tags

    def get_recommendations_for_user(
        self,
        user_id: str | None = None,
        limit: int = 50,
        workplace_type: str | None = None,
        hybrid: bool = False,
    ) -> list[JobRecommendationItem]:
        if not user_id:
            return []

        resume = self.repo.get_latest_by_user_id(user_id)
        if not resume:
            return []

        all_jobs = self.job_client.list_jobs()
        if not all_jobs:
            return []

        skipped_ids = self.interactions.get_user_skipped_job_ids(user_id)
        liked_ids = self.interactions.get_user_liked_job_ids(user_id)

        # Build liked skills set for swipe feedback boosting
        liked_skills: set[str] = set()
        for lj_id in liked_ids:
            j_obj = self.job_client.get_job(lj_id)
            if j_obj:
                liked_skills.update(j_obj.skills)

        recommendations: list[JobRecommendationItem] = []
        engine_tag = "hybrid-v1" if hybrid else self.generated_by

        for job in all_jobs:
            # Exclude skipped jobs
            if job.job_id in skipped_ids:
                continue

            # Workplace type filter
            if workplace_type:
                wp_clean = workplace_type.lower().strip()
                if wp_clean == "remote" and not (job.remote or "remote" in job.location.lower()):
                    continue
                elif wp_clean == "on-site" and (job.remote or "remote" in job.location.lower()):
                    continue

            blended_score, _, semantic_score, missing_skills, _ = self.scoring_engine.calculate_detailed_blended_score(
                resume, job
            )
            candidate_skills = set(resume.parsed_skills)

            # Normalize job skills for robust matching
            norm_job_skills = skill_extractor.normalize_skills(job.skills)
            matched_skills = [s for s in norm_job_skills if s in candidate_skills]

            if hybrid:
                final_score = round(blended_score * 0.60 + semantic_score * 0.40, 1)
            else:
                final_score = blended_score

            # Swipe feedback interaction boost: +10% if job overlaps with liked/saved job skills
            if liked_skills and any(s in liked_skills for s in job.skills):
                final_score = round(min(100.0, final_score + 10.0), 1)

            reason_tags = self.generate_reason_tags(resume, job, final_score, matched_skills)

            recommendations.append(
                JobRecommendationItem(
                    job_id=job.job_id,
                    match_percentage=final_score,
                    generated_by=engine_tag,
                    reason_tags=reason_tags,
                )
            )

        recommendations.sort(key=lambda item: (-item.match_percentage, item.job_id))
        return recommendations[:limit]

    def get_match_breakdown(
        self, user_id: str, job_id: str
    ) -> MatchBreakdownResponse | None:
        resume = self.repo.get_latest_by_user_id(user_id)
        job = self.job_client.get_job(job_id)
        if not resume or not job:
            return None

        blended_score, keyword_score, semantic_score, missing_skills, missing_keywords = (
            self.scoring_engine.calculate_detailed_blended_score(resume, job)
        )

        candidate_skills = set(resume.parsed_skills)
        norm_job_skills = skill_extractor.normalize_skills(job.skills)

        # Calculate exact matched vs missing skills using canonical taxonomy
        matched_skills = sorted([s for s in norm_job_skills if s in candidate_skills])

        total_job_skills = max(1, len(norm_job_skills))
        skill_overlap_pct = round((len(matched_skills) / total_job_skills) * 100.0, 1)
        keyword_overlap_pct = round(max(0.0, (keyword_score - skill_overlap_pct * 0.70) / 0.30), 1)

        overall_score = blended_score
        reason_tags = self.generate_reason_tags(resume, job, overall_score, matched_skills)

        if missing_skills:
            recommendation = f"To reach 80%+ match score, acquire or highlight: {', '.join(missing_skills[:3])}."
        else:
            recommendation = "Excellent match! Your skill set aligns directly with this job posting."

        return MatchBreakdownResponse(
            job_id=job.job_id,
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
