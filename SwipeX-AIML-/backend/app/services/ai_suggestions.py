from fastapi import HTTPException, status

from backend.app.models.schemas import AISuggestionResponse, JobDetail, ResumeRecord
from backend.app.services.ats_scorer import ATSScoringEngine, ats_scoring_engine
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo


class AISuggestionsEngine:
    """Milestone 3 Day 5: AI Resume Optimization Suggestions Engine.

    Generates actionable, targeted resume improvement recommendations to reach an 80%+ ATS match score.
    Features a 100% free rule-based template generator fallback requiring zero paid LLM API subscriptions.
    """

    def __init__(
        self,
        resume_repository: ResumeRepository = resume_repo,
        job_client: JobServiceClient = job_service_client,
        scoring_engine: ATSScoringEngine = ats_scoring_engine,
        target_threshold: float = 80.0,
    ):
        self.repo = resume_repository
        self.job_client = job_client
        self.scoring_engine = scoring_engine
        self.target_threshold = target_threshold

    def generate_suggestions(
        self, resume: ResumeRecord, job: JobDetail
    ) -> tuple[list[str], list[str], list[str]]:
        blended_score, keyword_score, semantic_score, missing_skills, missing_keywords = (
            self.scoring_engine.calculate_detailed_blended_score(resume, job)
        )

        suggestions: list[str] = []

        if missing_skills:
            top_skills = ", ".join(missing_skills[:3])
            suggestions.append(
                f"High-Impact Skill Gap: Add experience or projects highlighting '{top_skills}' to your resume."
            )

        if missing_keywords:
            top_kw = ", ".join(missing_keywords[:3])
            suggestions.append(
                f"Contextual Terminology: Incorporate key job terms like '{top_kw}' into your bullet points."
            )

        if blended_score < 50.0:
            suggestions.append(
                "Resume Structuring: Re-organize your work history to lead with technical responsibilities relevant to this role."
            )
        elif blended_score < self.target_threshold:
            suggestions.append(
                f"Target Match Boost: Your ATS score is {blended_score}%. Addressing missing skills will help you cross the {self.target_threshold}% interview threshold."
            )
        else:
            suggestions.append(
                f"Strong Alignment: Your resume scores {blended_score}%, exceeding the {self.target_threshold}% target threshold!"
            )

        return suggestions, missing_skills, missing_keywords

    def get_suggestions_for_resume(self, resume_id: str, job_id: str) -> AISuggestionResponse:
        resume = self.repo.get_by_id(resume_id)
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Resume with ID '{resume_id}' not found.",
            )

        job = self.job_client.get_job(job_id)
        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job with ID '{job_id}' not found.",
            )

        blended_score, _, _, missing_skills, missing_keywords = (
            self.scoring_engine.calculate_detailed_blended_score(resume, job)
        )
        suggestions, missing_skills, missing_keywords = self.generate_suggestions(resume, job)

        return AISuggestionResponse(
            resume_id=resume_id,
            job_id=job_id,
            current_ats_score=blended_score,
            target_threshold=self.target_threshold,
            suggestions=suggestions,
            missing_skills=missing_skills if blended_score < self.target_threshold else [],
            missing_keywords=missing_keywords if blended_score < self.target_threshold else [],
            generated_by="llm-fallback-v1",
        )


ai_suggestions_engine = AISuggestionsEngine()
