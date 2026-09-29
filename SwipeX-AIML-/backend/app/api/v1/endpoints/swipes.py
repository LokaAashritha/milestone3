from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.app.models.schemas import SwipeInteractionRequest, SwipeInteractionResponse
from backend.app.services.interaction_service import InteractionService, interaction_service

router = APIRouter(tags=["Swipe & User Feedback Intelligence"])


@router.post(
    "/swipe",
    response_model=SwipeInteractionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Record candidate swipe interaction",
    description="Records a swipe action ('like', 'save', or 'skip') for a candidate profile against a target job to dynamically refine recommendation ranking.",
)
def record_swipe_action(
    payload: SwipeInteractionRequest,
    x_user_id: str | None = Header(
        None, alias="X-User-ID", description="Optional user ID from Auth Gateway header"
    ),
    service: InteractionService = Depends(lambda: interaction_service),
) -> SwipeInteractionResponse:
    user_id = payload.user_id or x_user_id
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id must be provided in request body or X-User-ID header.",
        )
    try:
        return service.record_swipe(user_id=user_id, job_id=payload.job_id, action=payload.action)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err)
        )
