from fastapi import APIRouter, Depends, Header, Query, status

from backend.app.models.schemas import CareerIntelligenceResponse
from backend.app.services.career_intelligence import (
    CareerIntelligenceService,
    career_intelligence_service,
)

router = APIRouter(tags=["Career Intelligence & Skill Gap Analytics"])


@router.get(
    "/career-intelligence",
    response_model=CareerIntelligenceResponse,
    status_code=status.HTTP_200_OK,
    summary="Get personalized career readiness and skill gap insights",
    description="Analyzes the candidate's parsed resume against all 296+ active job market postings to compute readiness score, missing in-demand skills, and salary fit.",
)
def get_career_intelligence(
    user_id: str | None = Query(None, description="User ID to retrieve insights for"),
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    service: CareerIntelligenceService = Depends(lambda: career_intelligence_service),
) -> CareerIntelligenceResponse:
    resolved_user_id = user_id or x_user_id or "anonymous_user"
    return service.generate_career_intelligence(user_id=resolved_user_id)
