import re

from fastapi import HTTPException, status

from backend.app.core.config import settings
from backend.app.models.schemas import (
    ATSScoreResponse,
    JobDetail,
    ResumeRecord,
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


class ATSScoringEngine:
    """
    SwipeX Milestone 3 - Real ATS Scoring Engine.

    Scoring:
        1. Skill overlap
        2. Job-description keyword overlap
        3. Semantic similarity

    Final score:
        50% keyword score
        50% semantic similarity

    Keyword score:
        70% required-skill overlap
        30% description-keyword overlap

    Data ownership:
        - Resume data -> Job Data Service
        - Job data -> Job Data Service
        - ATS calculation -> AIML Service

    No mock/fallback ATS calculation is used.
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

    # ------------------------------------------------------------------
    # Job keyword extraction
    # ------------------------------------------------------------------

    def _extract_job_keywords(
        self,
        job: JobDetail,
    ) -> set[str]:
        stopwords = {
            "a",
            "an",
            "the",
            "and",
            "or",
            "in",
            "on",
            "at",
            "to",
            "for",
            "with",
            "is",
            "are",
            "was",
            "were",
            "be",
            "been",
            "will",
            "we",
            "you",
            "our",
            "looking",
            "seeking",
            "experienced",
            "join",
            "team",
            "responsibilities",
            "experience",
            "years",
            "work",
            "candidate",
            "role",
            "position",
            "must",
            "have",
            "ability",
            "strong",
            "knowledge",
            "understanding",
        }

        text = (
            f"{job.title} {job.description}"
        ).lower()

        words = re.findall(
            r"\b[a-z0-9+#.-]{3,}\b",
            text,
        )

        return {
            word
            for word in words
            if word not in stopwords
        }

    # ------------------------------------------------------------------
    # Simple score compatibility method
    # ------------------------------------------------------------------

    def calculate_score(
        self,
        resume: ResumeRecord,
        job: JobDetail,
    ) -> tuple[float, list[str]]:
        (
            blended_score,
            _keyword_score,
            _semantic_score,
            missing_skills,
            _missing_keywords,
        ) = self.calculate_detailed_blended_score(
            resume,
            job,
        )

        return blended_score, missing_skills

    # ------------------------------------------------------------------
    # Keyword compatibility method
    # ------------------------------------------------------------------

    def calculate_detailed_keyword_score(
        self,
        resume: ResumeRecord,
        job: JobDetail,
    ) -> tuple[float, list[str], list[str]]:
        (
            blended_score,
            _keyword_score,
            _semantic_score,
            missing_skills,
            missing_keywords,
        ) = self.calculate_detailed_blended_score(
            resume,
            job,
        )

        return (
            blended_score,
            missing_skills,
            missing_keywords,
        )

    # ------------------------------------------------------------------
    # Main ATS calculation
    # ------------------------------------------------------------------

    def calculate_detailed_blended_score(
        self,
        resume: ResumeRecord,
        job: JobDetail,
    ) -> tuple[
        float,
        float,
        float,
        list[str],
        list[str],
    ]:
        """
        Returns:

            blended_score
            keyword_score
            semantic_score
            missing_skills
            missing_keywords
        """

        # ==============================================================
        # 1. Normalize resume skills
        # ==============================================================

        resume_skills = (
            resume.parsed_skills
            or []
        )

        normalized_resume_skills = (
            skill_extractor.normalize_skills(
                resume_skills
            )
        )

        resume_skills_set = set(
            normalized_resume_skills
        )

        # ==============================================================
        # 2. Normalize job skills
        # ==============================================================

        job_skills = (
            job.skills
            or []
        )

        job_skills_normalized = (
            skill_extractor.normalize_skills(
                job_skills
            )
        )

        job_skills_set = set(
            job_skills_normalized
        )

        # ==============================================================
        # 3. Required-skill overlap
        # ==============================================================

        if job_skills_set:

            matched_skills = (
                resume_skills_set.intersection(
                    job_skills_set
                )
            )

            skill_ratio = (
                len(matched_skills)
                / len(job_skills_set)
            )

            missing_skills = sorted(
                job_skills_set
                - resume_skills_set
            )

        else:

            skill_ratio = 1.0
            missing_skills = []

        # ==============================================================
        # 4. Job description keyword overlap
        # ==============================================================

        job_keywords = (
            self._extract_job_keywords(job)
        )

        resume_text = (
            resume.raw_text
            or ""
        )

        resume_text_lower = (
            resume_text.lower()
        )

        if job_keywords:

            matched_keywords = {
                keyword
                for keyword in job_keywords
                if re.search(
                    r"\b"
                    + re.escape(keyword)
                    + r"\b",
                    resume_text_lower,
                )
            }

            keyword_ratio = (
                len(matched_keywords)
                / len(job_keywords)
            )

            missing_keywords = sorted(
                job_keywords
                - matched_keywords
            )[:10]

        else:

            keyword_ratio = 1.0
            missing_keywords = []

        # ==============================================================
        # 5. Keyword score
        #
        # 70% skills
        # 30% description keywords
        # ==============================================================

        raw_keyword_score = (
            (
                skill_ratio
                * self.skills_weight
            )
            +
            (
                keyword_ratio
                * self.keyword_weight
            )
        ) * 100.0

        keyword_score = round(
            min(
                max(
                    raw_keyword_score,
                    0.0,
                ),
                100.0,
            ),
            1,
        )

        # ==============================================================
        # 6. Semantic similarity
        # ==============================================================

        job_full_text = (
            f"{job.title}. "
            f"{job.description}"
        )

        semantic_score = (
            self.semantic_engine.calculate_similarity(
                resume_text,
                job_full_text,
            )
        )

        semantic_score = round(
            min(
                max(
                    float(semantic_score),
                    0.0,
                ),
                100.0,
            ),
            1,
        )

        # ==============================================================
        # 7. Final blended score
        #
        # 50% keyword
        # 50% semantic
        # ==============================================================

        blended_raw = (
            keyword_score
            * self.blended_kw_weight
        ) + (
            semantic_score
            * self.blended_sem_weight
        )

        blended_score = round(
            min(
                max(
                    blended_raw,
                    0.0,
                ),
                100.0,
            ),
            1,
        )

        return (
            blended_score,
            keyword_score,
            semantic_score,
            missing_skills,
            missing_keywords,
        )

    # ------------------------------------------------------------------
    # ATS score using canonical Job Data records
    # ------------------------------------------------------------------

    def get_ats_score(
        self,
        resume_id: str,
        job_id: str,
    ) -> ATSScoreResponse:
        """
        Calculate ATS score using canonical records from
        Job Data Service.

        This method is used by the AIML resume ATS endpoint.
        """

        resume = self.repo.get_by_id(
            resume_id
        )

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Resume with ID "
                    f"'{resume_id}' not found."
                ),
            )

        job = self.job_client.get_job(
            job_id
        )

        if not job:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Job with ID "
                    f"'{job_id}' not found."
                ),
            )

        (
            match_score,
            _keyword_score,
            _semantic_score,
            missing_skills,
            missing_keywords,
        ) = self.calculate_detailed_blended_score(
            resume,
            job,
        )

        if match_score >= self.threshold:

            overall_feedback = (
                f"Strong alignment! "
                f"Your ATS score is "
                f"{match_score}%, exceeding the "
                f"{self.threshold}% target threshold."
            )

            returned_missing_skills = []
            returned_missing_keywords = []

        else:

            top_gaps = (
                ", ".join(
                    missing_skills[:3]
                )
                if missing_skills
                else "key requirements"
            )

            overall_feedback = (
                f"ATS match score is "
                f"{match_score}%. "
                f"Key missing skill gaps: "
                f"{top_gaps}."
            )

            returned_missing_skills = (
                missing_skills
            )

            returned_missing_keywords = (
                missing_keywords
            )

        return ATSScoreResponse(
            match_score=match_score,
            missing_skills=(
                returned_missing_skills
            ),
            missing_keywords=(
                returned_missing_keywords
            ),
            overall_feedback=(
                overall_feedback
            ),
            generated_by=(
                self.generated_by
            ),
        )

    # ------------------------------------------------------------------
    # Raw-data ATS calculation
    # ------------------------------------------------------------------

    def calculate_from_raw_data(
        self,
        resume_text: str,
        resume_skills: list[str],
        job_description: str,
        job_skills: list[str],
    ) -> dict:
        """
        Calculate a real ATS score from already supplied resume/job data.

        This method is used when another internal service has already
        retrieved the canonical records and wants AIML to perform only
        the AI/ML calculation.
        """

        parsed_skills = (
            resume_skills
            if resume_skills
            else skill_extractor.extract_skills(
                resume_text
            )
        )

        temp_resume = ResumeRecord(
            resume_id="gateway-request",
            original_filename="resume",
            file_path="",
            file_type=".txt",
            raw_text=resume_text or "",
            parsed_skills=parsed_skills,
        )

        temp_job = JobDetail(
            job_id="gateway-request",
            title="",
            company="",
            description=(
                job_description or ""
            ),
            skills=(
                job_skills or []
            ),
        )

        (
            match_score,
            keyword_score,
            semantic_score,
            missing_skills,
            missing_keywords,
        ) = self.calculate_detailed_blended_score(
            temp_resume,
            temp_job,
        )

        if match_score >= self.threshold:

            overall_feedback = (
                f"Strong alignment! "
                f"Your ATS score is "
                f"{match_score}%, exceeding the "
                f"{self.threshold}% target threshold."
            )

            returned_missing_skills = []
            returned_missing_keywords = []

        else:

            top_gaps = (
                ", ".join(
                    missing_skills[:3]
                )
                if missing_skills
                else "key requirements"
            )

            overall_feedback = (
                f"ATS match score is "
                f"{match_score}%. "
                f"Key missing skill gaps: "
                f"{top_gaps}."
            )

            returned_missing_skills = (
                missing_skills
            )

            returned_missing_keywords = (
                missing_keywords
            )

        return {
            "match_score": match_score,
            "overall_score": match_score,
            "skill_score": round(
                (
                    (
                        len(
                            set(
                                skill_extractor.normalize_skills(
                                    parsed_skills
                                )
                            )
                            & set(
                                skill_extractor.normalize_skills(
                                    job_skills or []
                                )
                            )
                        )
                        / max(
                            1,
                            len(
                                set(
                                    skill_extractor.normalize_skills(
                                        job_skills or []
                                    )
                                )
                            ),
                        )
                    )
                    * 100.0
                ),
                1,
            ),
            "keyword_score": keyword_score,
            "semantic_match_score": semantic_score,
            "semantic_score": semantic_score,
            "missing_skills": (
                returned_missing_skills
            ),
            "missing_keywords": (
                returned_missing_keywords
            ),
            "overall_feedback": (
                overall_feedback
            ),
            "generated_by": (
                self.generated_by
            ),
        }


ats_scoring_engine = ATSScoringEngine()


def calculate_ats_score(
    resume_text: str,
    job_description: str,
    job_skills: list[str],
) -> dict:
    """
    Backward-compatible helper.

    Performs the real AIML ATS calculation without using
    mock data.
    """

    parsed_skills = (
        skill_extractor.extract_skills(
            resume_text
        )
    )

    return (
        ats_scoring_engine.calculate_from_raw_data(
            resume_text=resume_text,
            resume_skills=parsed_skills,
            job_description=job_description,
            job_skills=job_skills,
        )
    )