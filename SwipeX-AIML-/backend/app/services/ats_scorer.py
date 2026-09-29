import re

from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.schemas import ATSScoreResponse, JobDetail, ResumeRecord
from backend.app.services.job_service_client import JobServiceClient, job_service_client
from backend.app.services.resume_parser import ResumeRepository, resume_repo
from backend.app.services.semantic_engine import SemanticMatchingEngine, semantic_matching_engine
from backend.app.services.skill_extractor import skill_extractor


class ATSScoringEngine:
    """Milestone 3 Day 4: Blended ATS Scoring Engine (Keyword + Semantic).

    Blends 50% keyword match score (70% skill overlap + 30% description keywords) with 50% vector embedding
    semantic similarity score. Detects missing skills and missing description keywords when the score falls below 80%.
    """

    def __init__(
        self,
        resume_repository: ResumeRepository = resume_repo,
        job_client: JobServiceClient = job_service_client,
        semantic_engine: SemanticMatchingEngine = semantic_matching_engine,
        skills_weight: float = settings.REQUIRED_SKILLS_WEIGHT,
        keyword_weight: float = settings.KEYWORD_OVERLAP_WEIGHT,
        blended_kw_weight: float = settings.BLENDED_KEYWORD_WEIGHT,
        blended_sem_weight: float = settings.BLENDED_SEMANTIC_WEIGHT,
        threshold: float = settings.ATS_TARGET_THRESHOLD,
    ):
        self.repo = resume_repository
        self.job_client = job_client
        self.semantic_engine = semantic_engine
        self.skills_weight = skills_weight
        self.keyword_weight = keyword_weight
        self.blended_kw_weight = blended_kw_weight
        self.blended_sem_weight = blended_sem_weight
        self.threshold = threshold
        self.generated_by = settings.GENERATED_BY_TAG

    def _extract_job_keywords(self, job: JobDetail) -> set[str]:
        stopwords = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with", "is", "are",
            "was", "were", "be", "been", "will", "we", "you", "our", "looking", "seeking",
            "experienced", "join", "team", "responsibilities", "experience", "years", "work",
            "candidate", "role", "position", "must", "have", "ability", "strong", "knowledge",
            "understanding",
        }
        text = f"{job.title} {job.description}".lower()
        words = re.findall(r"\b[a-z0-9+#.-]{3,}\b", text)
        keywords = {w for w in words if w not in stopwords}
        return keywords

    def calculate_score(self, resume: ResumeRecord, job: JobDetail) -> tuple[float, list[str]]:
        blended_score, _, _, missing_skills, _ = self.calculate_detailed_blended_score(resume, job)
        return blended_score, missing_skills

    def calculate_detailed_keyword_score(
        self, resume: ResumeRecord, job: JobDetail
    ) -> tuple[float, list[str], list[str]]:
        blended_score, _, _, missing_skills, missing_keywords = self.calculate_detailed_blended_score(resume, job)
        return blended_score, missing_skills, missing_keywords

    def calculate_detailed_blended_score(
        self, resume: ResumeRecord, job: JobDetail
    ) -> tuple[float, float, float, list[str], list[str]]:
        resume_skills_set = set(resume.parsed_skills)
        job_skills_normalized = skill_extractor.normalize_skills(job.skills)
        job_skills_set = set(job_skills_normalized)

        if job_skills_set:
            matched_skills = resume_skills_set.intersection(job_skills_set)
            skill_ratio = len(matched_skills) / len(job_skills_set)
            missing_skills = sorted(job_skills_set - resume_skills_set)
        else:
            skill_ratio = 1.0
            missing_skills = []

        job_keywords = self._extract_job_keywords(job)
        resume_text_lower = resume.raw_text.lower()

        if job_keywords:
            matched_keywords = {
                kw
                for kw in job_keywords
                if re.search(r"\b" + re.escape(kw) + r"\b", resume_text_lower)
            }
            keyword_ratio = len(matched_keywords) / len(job_keywords)
            missing_keywords = sorted(job_keywords - matched_keywords)[:10]
        else:
            keyword_ratio = 1.0
            missing_keywords = []

        raw_kw_score = ((skill_ratio * self.skills_weight) + (keyword_ratio * self.keyword_weight)) * 100.0
        keyword_score = round(min(max(raw_kw_score, 0.0), 100.0), 1)

        job_full_text = f"{job.title}. {job.description}"
        semantic_score = self.semantic_engine.calculate_similarity(resume.raw_text, job_full_text)

        blended_raw = (keyword_score * self.blended_kw_weight) + (semantic_score * self.blended_sem_weight)
        blended_score = round(min(max(blended_raw, 0.0), 100.0), 1)

        return blended_score, keyword_score, semantic_score, missing_skills, missing_keywords

    def get_ats_score(self, resume_id: str, job_id: str) -> ATSScoreResponse:
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

        match_score, _, _, missing_skills, missing_keywords = self.calculate_detailed_blended_score(resume, job)

        if match_score >= self.threshold:
            overall_feedback = f"Strong alignment! Your ATS score is {match_score}%, exceeding the {self.threshold}% target threshold."
            m_skills = None
            m_keywords = None
        else:
            top_gaps = ", ".join(missing_skills[:3]) if missing_skills else "key requirements"
            overall_feedback = f"ATS match score is {match_score}%. Key missing skill gaps: {top_gaps}."
            m_skills = missing_skills
            m_keywords = missing_keywords

        return ATSScoreResponse(
            match_score=match_score,
            missing_skills=m_skills,
            missing_keywords=m_keywords,
            overall_feedback=overall_feedback,
            generated_by=self.generated_by,
        )


ats_scoring_engine = ATSScoringEngine()


def calculate_ats_score(
    resume_text: str,
    job_description: str,
    job_skills: list[str],
) -> dict:
    """Helper function requested by Backend & Identity Management.

    Accepts raw text & job info, returning dict with match_score, missing_skills, missing_keywords, overall_feedback.
    """
    parsed_skills = skill_extractor.extract_skills(resume_text)
    temp_resume = ResumeRecord(
        resume_id="temp_res",
        original_filename="resume.pdf",
        file_path="/tmp/resume.pdf",
        file_type=".pdf",
        raw_text=resume_text,
        parsed_skills=parsed_skills,
    )
    temp_job = JobDetail(
        job_id="temp_job",
        title="",
        company="",
        description=job_description,
        skills=job_skills,
    )
    match_score, _, _, missing_skills, missing_keywords = ats_scoring_engine.calculate_detailed_blended_score(
        temp_resume, temp_job
    )

    if match_score >= ats_scoring_engine.threshold:
        overall_feedback = f"Strong alignment! Your ATS score is {match_score}%, exceeding the {ats_scoring_engine.threshold}% target threshold."
        m_skills = None
        m_keywords = None
    else:
        top_gaps = ", ".join(missing_skills[:3]) if missing_skills else "key requirements"
        overall_feedback = f"ATS match score is {match_score}%. Key missing skill gaps: {top_gaps}."
        m_skills = missing_skills
        m_keywords = missing_keywords

    return {
        "match_score": match_score,
        "missing_skills": m_skills,
        "missing_keywords": m_keywords,
        "overall_feedback": overall_feedback,
        "generated_by": ats_scoring_engine.generated_by,
    }
