from datetime import datetime, timezone
from pydantic import BaseModel, ConfigDict, Field


class ResumeUploadResponse(BaseModel):
    resume_id: str = Field(..., description="Unique identifier of the stored resume")
    parsed_skills: list[str] = Field(
        default_factory=list, description="List of normalized skills extracted from the resume"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "resume_id": "res_8f7b2c1a4e90",
                "parsed_skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Git"],
            }
        }
    )


class ATSScoreResponse(BaseModel):
    match_score: float = Field(
        ..., ge=0, le=100, description="Blended ATS compatibility score between 0 and 100"
    )
    missing_skills: list[str] | None = Field(
        default=None, description="Required job skills missing from candidate resume (populated when match_score < 80%)"
    )
    missing_keywords: list[str] | None = Field(
        default=None, description="Job keywords missing from candidate resume (populated when match_score < 80%)"
    )
    overall_feedback: str | None = Field(
        default=None, description="Concise feedback summary explaining score and gap areas"
    )
    generated_by: str = Field(
        default="blended-v2", description="Model or engine identifier generating this score"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "match_score": 78.5,
                "missing_skills": ["Docker", "Kubernetes"],
                "missing_keywords": ["CI/CD pipeline", "microservices"],
                "overall_feedback": "Strong skill match, but missing containerization experience.",
                "generated_by": "blended-v2",
            }
        }
    )



class JobRecommendationItem(BaseModel):
    job_id: str = Field(..., description="Unique identifier of the recommended job")
    match_percentage: float = Field(
        ..., ge=0, le=100, description="Overall heuristic match percentage for the candidate"
    )
    generated_by: str = Field(
        default="heuristic-v0", description="Engine version producing the recommendation"
    )
    reason_tags: list[str] = Field(
        default_factory=list, description="Descriptive tags explaining why this job was recommended"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "job_id": "job_dev_101",
                "match_percentage": 88.0,
                "generated_by": "heuristic-v0",
                "reason_tags": ["Matches 85% of your skills", "High Python & FastAPI overlap", "Remote opportunity"],
            }
        }
    )


class ResumeRecord(BaseModel):
    resume_id: str
    user_id: str | None = None
    original_filename: str
    file_path: str
    file_type: str
    raw_text: str
    parsed_skills: list[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class JobDetail(BaseModel):
    job_id: str
    title: str
    company: str
    type: str = "Full-time"
    location: str = "Remote"
    remote: bool = True
    salary_range: str | None = "$90,000 - $130,000"
    skills: list[str] = Field(default_factory=list)
    description: str = ""
    posted_at: str | None = None


class SwipeInteractionRequest(BaseModel):
    user_id: str = Field(..., description="Candidate user ID")
    job_id: str = Field(..., description="Target job ID")
    action: str = Field(..., description="Swipe action: 'like', 'save', or 'skip'")


class SwipeInteractionResponse(BaseModel):
    status: str = "success"
    user_id: str
    job_id: str
    action: str
    recorded_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MatchBreakdownResponse(BaseModel):
    job_id: str
    job_title: str
    company_name: str
    overall_match_percentage: float
    skill_overlap_percentage: float
    keyword_overlap_percentage: float
    semantic_similarity_percentage: float
    matched_skills: list[str]
    missing_skills: list[str]
    reason_tags: list[str]
    career_recommendation: str
    generated_by: str = "hybrid-v1"


class CareerIntelligenceResponse(BaseModel):
    user_id: str
    readiness_score: float = Field(..., ge=0, le=100, description="Overall market readiness score")
    total_matched_skills_count: int
    top_matched_skills: list[str]
    top_missing_in_demand_skills: list[str]
    estimated_salary_fit: str
    recommended_actions: list[str]
    generated_by: str = "career-intel-v1"


class BlendedATSScoreResponse(BaseModel):
    match_score: float = Field(..., ge=0, le=100, description="Blended ATS score (keyword + semantic)")
    keyword_score: float = Field(..., ge=0, le=100, description="Exact keyword match score")
    semantic_score: float = Field(..., ge=0, le=100, description="Dense vector semantic similarity score")
    missing_skills: list[str] = Field(default_factory=list, description="Missing required job skills")
    missing_keywords: list[str] = Field(default_factory=list, description="Missing contextual description keywords")
    ai_suggestions: list[str] = Field(default_factory=list, description="AI-generated optimization bullet points")
    generated_by: str = Field(default="blended-v2", description="Engine identifier")


class AISuggestionResponse(BaseModel):
    resume_id: str
    job_id: str
    current_ats_score: float
    target_threshold: float = 80.0
    suggestions: list[str] = Field(default_factory=list, description="Targeted actionable improvement advice")
    missing_skills: list[str] = Field(default_factory=list)
    missing_keywords: list[str] = Field(default_factory=list)
    generated_by: str = "llm-fallback-v1"


class ResumeVersionItem(BaseModel):
    resume_id: str
    version_number: int = 1
    original_filename: str
    file_type: str
    parsed_skills_count: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ErrorResponse(BaseModel):
    detail: str
    error_code: str | None = None


