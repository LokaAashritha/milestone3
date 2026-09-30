from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import requests
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.models.schemas import SwipeInteractionResponse


class SwipeRecord(BaseModel):
    user_id: str
    job_id: str
    action: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class InteractionService:
    """
    Reads/writes swipe interactions through the Job Data Service.

    Job Data Service is the source of truth for swipe history.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: int = 15,
    ) -> None:
        self.base_url = (
            base_url or settings.JOB_DATA_SERVICE_URL
        ).rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"

        try:
            response = requests.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Job Data Service is unavailable at {self.base_url}: {exc}"
            ) from exc

        if response.status_code >= 400:
            try:
                detail = response.json()
            except Exception:
                detail = response.text

            raise RuntimeError(
                f"Job Data Service returned HTTP "
                f"{response.status_code}: {detail}"
            )

        try:
            return response.json()
        except ValueError as exc:
            raise RuntimeError(
                f"Invalid JSON response from Job Data Service: {url}"
            ) from exc

    # ------------------------------------------------------------------
    # Record swipe
    # ------------------------------------------------------------------

    def record_swipe(
        self,
        user_id: str,
        job_id: str,
        action: str,
    ) -> SwipeInteractionResponse:
        """
        Translate AIML's legacy action vocabulary into Job Data's
        persistent swipe vocabulary.
        """

        action_clean = action.lower().strip()

        action_mapping = {
            "like": ("right", "apply"),
            "save": ("right", "save"),
            "skip": ("left", "skip"),
        }

        if action_clean not in action_mapping:
            raise ValueError(
                "action must be one of: like, save, skip"
            )

        direction, action_type = action_mapping[action_clean]

        payload = {
            "job_id": int(job_id),
            "direction": direction,
            "action_type": action_type,
            "user_id": user_id,
        }

        data = self._request(
            "POST",
            "/swipes",
            json=payload,
            headers={
                "X-User-ID": user_id,
            },
        )

        return SwipeInteractionResponse(
            user_id=str(data.get("user_id", user_id)),
            job_id=str(data.get("job_id", job_id)),
            action=action_clean,
            message=data.get(
                "message",
                "Swipe interaction recorded successfully",
            ),
        )

    # ------------------------------------------------------------------
    # Get history
    # ------------------------------------------------------------------

    def get_user_swipes(
        self,
        user_id: str,
    ) -> list[SwipeRecord]:
        data = self._request(
            "GET",
            "/swipes/history",
            params={
                "user_id": user_id,
                "limit": 500,
            },
            headers={
                "X-User-ID": user_id,
            },
        )

        if not isinstance(data, list):
            return []

        records: list[SwipeRecord] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            job_id = item.get("job_id")

            action_type = str(
                item.get("action_type")
                or ""
            ).lower()

            # Convert persistent Job Data action types to the
            # vocabulary expected internally by AIML.
            if action_type == "apply":
                action = "like"
            elif action_type == "save":
                action = "save"
            elif action_type == "skip":
                action = "skip"
            else:
                continue

            swiped_at = item.get("swiped_at")

            try:
                if isinstance(swiped_at, str):
                    created_at = datetime.fromisoformat(
                        swiped_at.replace("Z", "+00:00")
                    )
                else:
                    created_at = datetime.now(timezone.utc)
            except ValueError:
                created_at = datetime.now(timezone.utc)

            records.append(
                SwipeRecord(
                    user_id=user_id,
                    job_id=str(job_id),
                    action=action,
                    created_at=created_at,
                )
            )

        return records

    # ------------------------------------------------------------------
    # Positive interactions
    # ------------------------------------------------------------------

    def get_user_liked_job_ids(
        self,
        user_id: str,
    ) -> set[str]:
        return {
            swipe.job_id
            for swipe in self.get_user_swipes(user_id)
            if swipe.action in ("like", "save")
        }

    # ------------------------------------------------------------------
    # Skipped jobs
    # ------------------------------------------------------------------

    def get_user_skipped_job_ids(
        self,
        user_id: str,
    ) -> set[str]:
        return {
            swipe.job_id
            for swipe in self.get_user_swipes(user_id)
            if swipe.action == "skip"
        }


interaction_service = InteractionService()