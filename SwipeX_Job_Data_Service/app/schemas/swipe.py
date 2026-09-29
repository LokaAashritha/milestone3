from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from app.models.swipe import SwipeDirection, SwipeActionType
from app.schemas.job import JobSummaryOut


class SwipeCreate(BaseModel):
    job_id: int
    direction: SwipeDirection  # "right" or "left"
    action_type: Optional[SwipeActionType] = None  # "apply", "save", or "skip"
    notes: Optional[str] = None
    user_id: Optional[str] = "demo-user-1"  # Defaults for standalone testing if auth token not provided


class SwipeOut(BaseModel):
    swipe_id: int
    user_id: str
    job_id: int
    direction: SwipeDirection
    action_type: SwipeActionType
    swiped_at: datetime
    message: str = "Swipe interaction recorded successfully"

    model_config = ConfigDict(from_attributes=True)


class SwipeHistoryItem(BaseModel):
    job_id: int
    direction: SwipeDirection
    action_type: SwipeActionType
    swiped_at: datetime
    job: Optional[JobSummaryOut] = None

    model_config = ConfigDict(from_attributes=True)


class SwipeSummaryOut(BaseModel):
    user_id: str
    total_swipes: int
    right_swipes: int
    left_swipes: int
    applied_count: int
    saved_count: int
    skipped_count: int
