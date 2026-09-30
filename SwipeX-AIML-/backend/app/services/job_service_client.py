from __future__ import annotations

from typing import Any

import requests

from backend.app.core.config import settings
from backend.app.models.schemas import JobDetail


class JobServiceClient:
    """
    HTTP client for the SwipeX Job & Data Intelligence Service.

    Job Data Service is the source of truth for jobs.
    AIML does not use seed_jobs.json for recommendations.
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

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

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
                f"Job Data Service returned invalid JSON for {url}"
            ) from exc

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    @staticmethod
    def _to_job_detail(item: dict[str, Any]) -> JobDetail:
        """
        Convert Job Data Service JobSummaryOut/JobDetailOut
        into the AIML JobDetail model.
        """

        job_id = item.get("job_id", item.get("id"))

        title = (
            item.get("title")
            or item.get("job_title")
            or ""
        )

        company_value = item.get("company", "")

        if isinstance(company_value, dict):
            company = (
                company_value.get("name")
                or company_value.get("company_name")
                or ""
            )
        else:
            company = str(company_value or "")

        description = (
            item.get("description")
            or item.get("job_description")
            or ""
        )

        skills = item.get("skills") or []
        required_skills = item.get("required_skills") or []

        if isinstance(skills, str):
            skills = [
                skill.strip()
                for skill in skills.split(",")
                if skill.strip()
            ]

        if isinstance(required_skills, str):
            required_skills = [
                skill.strip()
                for skill in required_skills.split(",")
                if skill.strip()
            ]

        # Combine skills and required_skills without duplicates.
        combined_skills: list[str] = []

        for skill in [*skills, *required_skills]:
            skill_clean = str(skill).strip()

            if skill_clean and skill_clean.lower() not in {
                existing.lower()
                for existing in combined_skills
            }:
                combined_skills.append(skill_clean)

        workplace_type = str(
            item.get("workplace_type")
            or ""
        )

        location = str(
            item.get("location")
            or "Remote"
        )

        remote = (
            workplace_type.lower() == "remote"
            or "remote" in location.lower()
        )

        salary_range = item.get("salary_range")

        if not salary_range:
            salary_min = item.get("salary_min")
            salary_max = item.get("salary_max")
            currency = item.get("salary_currency", "INR")

            if salary_min is not None and salary_max is not None:
                try:
                    salary_range = (
                        f"{currency} "
                        f"{int(salary_min):,} - "
                        f"{int(salary_max):,}"
                    )
                except (TypeError, ValueError):
                    salary_range = "Competitive"
            else:
                salary_range = "Competitive"

        return JobDetail(
            job_id=str(job_id),
            title=title,
            company=company,
            type=str(
                item.get("type")
                or item.get("job_type")
                or "Full-time"
            ),
            location=location,
            remote=remote,
            salary_range=str(salary_range),
            skills=combined_skills,
            description=description,
            posted_at=item.get("posted_at"),
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_job(self, job_id: str) -> JobDetail | None:
        """
        Get one real job from Job Data Service.
        """

        try:
            data = self._request(
                "GET",
                f"/jobs/{int(job_id)}",
            )
        except (ValueError, RuntimeError):
            return None

        if not isinstance(data, dict):
            return None

        return self._to_job_detail(data)

    def list_jobs(self) -> list[JobDetail]:
        """
        Get active jobs from the real Job Data Service.
        """

        data = self._request(
            "GET",
            "/jobs",
            params={
                "page": 1,
                "page_size": 100,
            },
        )

        if isinstance(data, dict):
            # Defensive handling if Job Data returns a wrapped response.
            items = (
                data.get("jobs")
                or data.get("items")
                or data.get("data")
                or []
            )
        elif isinstance(data, list):
            items = data
        else:
            items = []

        jobs: list[JobDetail] = []

        for item in items:
            if not isinstance(item, dict):
                continue

            try:
                jobs.append(self._to_job_detail(item))
            except Exception:
                # Ignore malformed individual records rather than
                # crashing the entire recommendation request.
                continue

        return jobs

    def add_or_update_job(self, job: JobDetail) -> None:
        """
        Deprecated compatibility method.

        Job creation/update belongs to Job Data Service.
        AIML must not maintain its own job database.
        """

        raise RuntimeError(
            "AIML cannot locally add or update jobs. "
            "Create or update jobs through the Job Data Service."
        )


job_service_client = JobServiceClient()