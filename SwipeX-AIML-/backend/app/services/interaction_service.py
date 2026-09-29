from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.app.models.schemas import SwipeInteractionResponse


class SwipeRecord(BaseModel):
    user_id: str
    job_id: str
    action: str  # "like", "save", "skip"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InteractionService:
    def __init__(self) -> None:
        self._user_swipes: dict[str, list[SwipeRecord]] = {}

    def record_swipe(self, user_id: str, job_id: str, action: str) -> SwipeInteractionResponse:
        action_clean = action.lower().strip()
        if action_clean not in ("like", "save", "skip"):
            raise ValueError(f"Invalid swipe action: '{action}'. Must be 'like', 'save', or 'skip'.")

        record = SwipeRecord(user_id=user_id, job_id=job_id, action=action_clean)
        if user_id not in self._user_swipes:
            self._user_swipes[user_id] = []

        # Remove any previous swipe for the same job to update it
        self._user_swipes[user_id] = [
            sw for sw in self._user_swipes[user_id] if sw.job_id != job_id
        ]
        self._user_swipes[user_id].append(record)

        return SwipeInteractionResponse(
            status="success",
            user_id=user_id,
            job_id=job_id,
            action=action_clean,
            recorded_at=record.created_at,
        )

    def get_user_swipes(self, user_id: str) -> list[SwipeRecord]:
        return self._user_swipes.get(user_id, [])

    def get_user_liked_job_ids(self, user_id: str) -> set[str]:
        return {sw.job_id for sw in self.get_user_swipes(user_id) if sw.action in ("like", "save")}

    def get_user_skipped_job_ids(self, user_id: str) -> set[str]:
        return {sw.job_id for sw in self.get_user_swipes(user_id) if sw.action == "skip"}


interaction_service = InteractionService()
