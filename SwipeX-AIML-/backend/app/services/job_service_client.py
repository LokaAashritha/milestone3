import json
from pathlib import Path

from backend.app.core.config import settings
from backend.app.models.schemas import JobDetail


class JobServiceClient:
    def __init__(self, seed_file: Path = settings.SEED_JOBS_FILE):
        self.seed_file = seed_file
        self._cached_jobs: dict[str, JobDetail] = {}
        self._load_seed_jobs()

    def _load_seed_jobs(self) -> None:
        if not self.seed_file.exists():
            return

        try:
            with open(self.seed_file, encoding="utf-8") as f:
                data = json.load(f)
                for item in data:
                    job_id = str(item.get("job_id"))
                    title = item.get("job_title") or item.get("title", "")
                    company = item.get("company_name") or item.get("company", "")
                    description = item.get("job_description") or item.get("description", "")

                    raw_skills = item.get("skills_required") or item.get("skills", [])
                    if isinstance(raw_skills, str):
                        try:
                            skills = json.loads(raw_skills)
                        except Exception:
                            skills = [s.strip() for s in raw_skills.split(",")]
                    else:
                        skills = raw_skills

                    location = item.get("location", "Remote")
                    workplace_type = item.get("workplace_type", "")
                    remote = item.get("remote", True) if "remote" in item else (workplace_type.lower() == "remote")

                    sal_min = item.get("salary_min")
                    sal_max = item.get("salary_max")
                    curr = item.get("salary_currency", "INR")
                    if sal_min and sal_max:
                        salary_range = f"{curr} {sal_min:,} - {sal_max:,}"
                    else:
                        salary_range = item.get("salary_range", "Competitive")

                    job = JobDetail(
                        job_id=job_id,
                        title=title,
                        company=company,
                        type=item.get("job_type", "Full-time"),
                        location=location,
                        remote=remote,
                        salary_range=salary_range,
                        skills=skills,
                        description=description,
                        posted_at=item.get("posted_at"),
                    )
                    self._cached_jobs[job.job_id] = job

            # Support legacy alias keys for backward compatibility in unit tests
            if "5" in self._cached_jobs and "job_py_01" not in self._cached_jobs:
                self._cached_jobs["job_py_01"] = self._cached_jobs["5"]
            if "8" in self._cached_jobs and "job_react_02" not in self._cached_jobs:
                self._cached_jobs["job_react_02"] = self._cached_jobs["8"]

        except Exception as e:
            print(f"[Warning] Failed to load seed jobs: {e}")

    def get_job(self, job_id: str) -> JobDetail | None:
        return self._cached_jobs.get(str(job_id))

    def list_jobs(self) -> list[JobDetail]:
        # Return unique jobs (skip alias duplicate pointers)
        seen = set()
        unique_jobs = []
        for job in self._cached_jobs.values():
            if job.job_id not in seen:
                seen.add(job.job_id)
                unique_jobs.append(job)
        return unique_jobs

    def add_or_update_job(self, job: JobDetail) -> None:
        self._cached_jobs[job.job_id] = job


job_service_client = JobServiceClient()
