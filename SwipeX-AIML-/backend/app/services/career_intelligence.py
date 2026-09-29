from collections import Counter

from backend.app.models.schemas import CareerIntelligenceResponse, ResumeRecord
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo


class CareerIntelligenceService:
    def __init__(
        self,
        job_client: JobServiceClient = job_service_client,
        repository: ResumeRepository = resume_repo,
    ) -> None:
        self.job_client = job_client
        self.repo = repository

    def generate_career_intelligence(
        self, user_id: str
    ) -> CareerIntelligenceResponse:
        resume: ResumeRecord | None = self.repo.get_latest_by_user_id(user_id)
        if not resume:
            return CareerIntelligenceResponse(
                user_id=user_id,
                readiness_score=0.0,
                total_matched_skills_count=0,
                top_matched_skills=[],
                top_missing_in_demand_skills=[],
                estimated_salary_fit="Upload a resume to analyze market salary fit",
                recommended_actions=["Upload your latest resume to receive personalized career insights."],
            )

        candidate_skills = set(resume.parsed_skills)
        all_jobs = self.job_client.list_jobs()

        skill_frequency: Counter[str] = Counter()
        matched_frequency: Counter[str] = Counter()
        missing_frequency: Counter[str] = Counter()

        for job in all_jobs:
            for skill in job.skills:
                skill_frequency[skill] += 1
                if skill in candidate_skills:
                    matched_frequency[skill] += 1
                else:
                    missing_frequency[skill] += 1

        top_missing = [s for s, _ in missing_frequency.most_common(5)]
        top_matched = [s for s, _ in matched_frequency.most_common(5)]

        # Calculate readiness score based on skill market coverage
        total_market_jobs = max(1, len(all_jobs))
        matching_job_count = sum(
            1 for job in all_jobs if any(s in candidate_skills for s in job.skills)
        )
        readiness_score = round(min(100.0, max(10.0, (matching_job_count / total_market_jobs) * 100.0)), 1)

        # Generate action items
        recommended_actions: list[str] = []
        if top_missing:
            recommended_actions.append(
                f"High-demand gap: Learning '{top_missing[0]}' will unlock up to {missing_frequency[top_missing[0]]} new job postings."
            )
        if len(top_missing) > 1:
            recommended_actions.append(
                f"Secondary skill focus: Add '{top_missing[1]}' to boost your ATS match percentage."
            )
        recommended_actions.append("Keep resume updated with recent project metrics and technical keywords.")

        salary_fit = "₹8,00,000 - ₹18,00,000 PA (INR)" if readiness_score >= 50 else "₹5,00,000 - ₹10,00,000 PA (INR)"

        return CareerIntelligenceResponse(
            user_id=user_id,
            readiness_score=readiness_score,
            total_matched_skills_count=len(candidate_skills),
            top_matched_skills=top_matched,
            top_missing_in_demand_skills=top_missing,
            estimated_salary_fit=salary_fit,
            recommended_actions=recommended_actions,
        )


career_intelligence_service = CareerIntelligenceService()
