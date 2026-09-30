from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    Query,
    UploadFile,
    status,
)

from backend.app.models.schemas import (
    AISuggestionResponse,
    ATSScoreResponse,
    ResumeUploadResponse,
)

from backend.app.services.ai_suggestions import (
    AISuggestionsEngine,
    ai_suggestions_engine,
)

from backend.app.services.ats_scorer import (
    ATSScoringEngine,
    ats_scoring_engine,
)

from backend.app.services.resume_parser import (
    ResumeParserService,
    resume_parser_service,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume & Career Intelligence"],
)


# ==========================================================================
# Resume Upload
# ==========================================================================

@router.post(
    "/upload",
    response_model=ResumeUploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and parse a candidate resume",
    description=(
        "Accepts a PDF, DOCX, or TXT resume file via "
        "multipart/form-data, parses the resume, stores the "
        "canonical resume through Job Data Service, extracts "
        "technical skills, and returns the assigned resume_id "
        "and parsed_skills."
    ),
)
async def upload_resume(
    file: UploadFile = File(
        ...,
        description="Resume file (.pdf, .docx, .txt)",
    ),
    user_id: str | None = Form(
        None,
        description=(
            "Optional user ID to associate "
            "with this resume"
        ),
    ),
    x_user_id: str | None = Header(
        None,
        alias="X-User-ID",
        description=(
            "Optional user ID supplied by "
            "the Gateway"
        ),
    ),
    parser: ResumeParserService = Depends(
        lambda: resume_parser_service
    ),
) -> ResumeUploadResponse:

    resolved_user_id = (
        user_id
        or x_user_id
    )

    response = (
        await parser.parse_and_store_upload(
            upload_file=file,
            user_id=resolved_user_id,
        )
    )

    return response


# ==========================================================================
# ATS Score
# ==========================================================================

@router.get(
    "/{resume_id}/ats-score",
    response_model=ATSScoreResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate blended ATS match score against a job",
    description=(
        "Calculates the real blended ATS compatibility "
        "score using required-skill overlap, job-description "
        "keyword overlap, and semantic similarity. "
        "Resume and job records are retrieved from the "
        "canonical Job Data Service."
    ),
)
def get_resume_ats_score(
    resume_id: str,
    job_id: str = Query(
        ...,
        description=(
            "ID of the target job. "
            "Job Data Service uses integer job IDs."
        ),
    ),
    scorer: ATSScoringEngine = Depends(
        lambda: ats_scoring_engine
    ),
) -> ATSScoreResponse:

    return scorer.get_ats_score(
        resume_id=resume_id,
        job_id=job_id,
    )


# ==========================================================================
# AI Resume Suggestions
# ==========================================================================

@router.get(
    "/{resume_id}/suggestions",
    response_model=AISuggestionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get AI-powered resume optimization suggestions",
    description=(
        "Generates resume improvement suggestions "
        "based on the real resume and target job data."
    ),
)
def get_resume_suggestions(
    resume_id: str,
    job_id: str = Query(
        ...,
        description="ID of the target job",
    ),
    engine: AISuggestionsEngine = Depends(
        lambda: ai_suggestions_engine
    ),
) -> AISuggestionResponse:

    return engine.get_suggestions_for_resume(
        resume_id=resume_id,
        job_id=job_id,
    )