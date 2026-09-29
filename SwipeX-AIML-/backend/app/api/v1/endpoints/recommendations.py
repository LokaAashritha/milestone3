from fastapi import APIRouter, Depends, Header, HTTPException, Query, status

from backend.app.models.schemas import JobRecommendationItem, MatchBreakdownResponse
from backend.app.services.recommendation_engine import (
    RecommendationEngine,
    recommendation_engine,
)

router = APIRouter(tags=["Recommendations & Career Intelligence"])


@router.get(
    "/recommendations",
    response_model=list[JobRecommendationItem],
    status_code=status.HTTP_200_OK,
    summary="Get heuristic job recommendations for a user",
    description="Returns a ranked list of job recommendations based on skill and keyword overlap between the user's latest uploaded resume and available jobs.",
)
def get_recommendations(
    user_id: str | None = Query(None, description="User ID to retrieve recommendations for"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of recommendations to return"),
    workplace_type: str | None = Query(None, description="Filter by workplace type: 'remote' or 'on-site'"),
    hybrid: bool = Query(False, description="Enable hybrid NLP semantic matching model (v1)"),
    engine: RecommendationEngine = Depends(lambda: recommendation_engine),
) -> list[JobRecommendationItem]:
    resolved_user_id = user_id or x_user_id
    return engine.get_recommendations_for_user(
        user_id=resolved_user_id, limit=limit, workplace_type=workplace_type, hybrid=hybrid
    )


@router.get(
    "/recommendations/breakdown",
    response_model=MatchBreakdownResponse,
    status_code=status.HTTP_200_OK,
    summary="Get detailed match telemetry breakdown for a candidate and job",
    description="Deconstructs match percentage into skill overlap, keyword overlap, semantic text similarity, and provides personalized learning recommendations.",
)
def get_recommendation_breakdown(
    job_id: str = Query(..., description="Target job ID"),
    user_id: str | None = Query(None, description="User ID to calculate match breakdown for"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    engine: RecommendationEngine = Depends(lambda: recommendation_engine),
) -> MatchBreakdownResponse:
    resolved_user_id = user_id or x_user_id
    if not resolved_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id must be provided via query param or X-User-ID header.",
        )
    breakdown = engine.get_match_breakdown(user_id=resolved_user_id, job_id=job_id)
    if not breakdown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Match breakdown could not be computed for user '{resolved_user_id}' and job '{job_id}'. Check that resume and job exist.",
        )
    return breakdown
