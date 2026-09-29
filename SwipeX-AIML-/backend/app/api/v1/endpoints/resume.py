from fastapi import APIRouter, Depends, File, Form, Header, Query, UploadFile, status

from backend.app.models.schemas import (
    AISuggestionResponse,
    ATSScoreResponse,
    ResumeUploadResponse,
)
from backend.app.services.ai_suggestions import AISuggestionsEngine, ai_suggestions_engine
from backend.app.services.ats_scorer import ATSScoringEngine, ats_scoring_engine
from backend.app.services.resume_parser import (
    ResumeParserService,
    resume_parser_service,
)

router = APIRouter(prefix="/resume", tags=["Resume & Career Intelligence"])


@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a candidate resume",
    description="Accepts a PDF, DOCX, or TXT resume file via multipart/form-data, securely stores it, extracts technical skills, and returns assigned resume_id and parsed_skills.",
)
async def upload_resume(
    file: UploadFile = File(..., description="Resume file (.pdf, .docx, .txt)"),
    user_id: str | None = Form(None, description="Optional user ID to associate with this resume"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    parser: ResumeParserService = Depends(lambda: resume_parser_service),
) -> ResumeUploadResponse:
    resolved_user_id = user_id or x_user_id
    response = await parser.parse_and_store_upload(upload_file=file, user_id=resolved_user_id)
    return response


@router.get(
    "/{resume_id}/ats-score",
    response_model=ATSScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate blended ATS match score against a job",
    description="Computes 50/50 blended ATS compatibility score (Keyword Overlap + Semantic Embedding Similarity) between resume and job, listing missing skills.",
)
def get_resume_ats_score(
    resume_id: str,
    job_id: str = Query(..., description="ID of the job to score against"),
    scorer: ATSScoringEngine = Depends(lambda: ats_scoring_engine),
) -> ATSScoreResponse:
    return scorer.get_ats_score(resume_id=resume_id, job_id=job_id)


@router.get(
    "/{resume_id}/suggestions",
    response_model=AISuggestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI-powered resume optimization suggestions",
    description="Generates actionable resume improvement recommendations to reach an 80%+ ATS match score with free rule-based fallback generator.",
)
def get_resume_suggestions(
    resume_id: str,
    job_id: str = Query(..., description="ID of the target job"),
    engine: AISuggestionsEngine = Depends(lambda: ai_suggestions_engine),
) -> AISuggestionResponse:
    return engine.get_suggestions_for_resume(resume_id=resume_id, job_id=job_id)
