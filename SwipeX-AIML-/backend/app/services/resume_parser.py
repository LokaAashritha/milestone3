from __future__ import annotations

import io
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pdfplumber
import pypdf
import requests
from docx import Document
from fastapi import HTTPException, UploadFile, status
from pydantic import BaseModel, Field

from backend.app.core.config import settings
from backend.app.models.schemas import ResumeRecord, ResumeUploadResponse
from backend.app.services.skill_extractor import skill_extractor


class ResumeRepository:
    """
    HTTP-backed resume repository.

    Job Data Service is the single source of truth for resumes.
    AIML no longer stores resumes in an in-memory dictionary.
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
        *,
        user_id: str | None = None,
        **kwargs: Any,
    ) -> Any:
        url = f"{self.base_url}/{path.lstrip('/')}"

        headers = kwargs.pop("headers", {}) or {}

        if user_id:
            headers["X-User-ID"] = user_id

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                timeout=self.timeout,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Job Data Service is unavailable at "
                f"{self.base_url}: {exc}"
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
                f"Job Data Service returned invalid JSON "
                f"for {url}"
            ) from exc

    @staticmethod
    def _to_resume_record(
        data: dict[str, Any],
    ) -> ResumeRecord:
        """
        Convert Job Data ResumeUploadOut/ResumeDetailOut
        into the AIML ResumeRecord model.
        """

        resume_id = str(
            data.get("id")
            or data.get("resume_id")
            or ""
        )

        user_id = data.get("user_id")

        file_name = (
            data.get("file_name")
            or data.get("original_filename")
            or "resume"
        )

        file_type = data.get("file_type") or "application/octet-stream"

        parsed_text = data.get("parsed_text") or ""

        extracted_skills = (
            data.get("extracted_skills")
            or []
        )

        if isinstance(extracted_skills, str):
            extracted_skills = [
                skill.strip()
                for skill in extracted_skills.split(",")
                if skill.strip()
            ]

        uploaded_at_value = data.get("uploaded_at")

        try:
            if isinstance(uploaded_at_value, str):
                uploaded_at = datetime.fromisoformat(
                    uploaded_at_value.replace("Z", "+00:00")
                )
            else:
                uploaded_at = datetime.now(timezone.utc)
        except ValueError:
            uploaded_at = datetime.now(timezone.utc)

        return ResumeRecord(
            resume_id=resume_id,
            user_id=str(user_id) if user_id else None,
            original_filename=file_name,
            file_path="",
            file_type=file_type,
            raw_text=parsed_text,
            parsed_skills=extracted_skills,
            created_at=uploaded_at,
        )

    def get_by_id(
        self,
        resume_id: str,
        user_id: str | None = None,
    ) -> ResumeRecord | None:
        try:
            data = self._request(
                "GET",
                f"/resumes/{resume_id}",
                user_id=user_id,
            )
        except RuntimeError:
            return None

        if not isinstance(data, dict):
            return None

        try:
            return self._to_resume_record(data)
        except Exception:
            return None

    def get_latest_by_user_id(
        self,
        user_id: str,
    ) -> ResumeRecord | None:
        """
        Retrieve the active/latest resume belonging to the user.
        """

        data = self._request(
            "GET",
            "/resumes",
            params={
                "active_only": True,
                "user_id": user_id,
            },
            user_id=user_id,
        )

        if not isinstance(data, list) or not data:
            return None

        records: list[ResumeRecord] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            try:
                records.append(
                    self._to_resume_record(item)
                )
            except Exception:
                continue

        if not records:
            return None

        records.sort(
            key=lambda resume: resume.created_at,
            reverse=True,
        )

        return records[0]

    def list_all(
        self,
        user_id: str | None = None,
    ) -> list[ResumeRecord]:
        params: dict[str, Any] = {}

        if user_id:
            params["user_id"] = user_id

        data = self._request(
            "GET",
            "/resumes",
            params=params,
            user_id=user_id,
        )

        if not isinstance(data, list):
            return []

        records: list[ResumeRecord] = []

        for item in data:
            if not isinstance(item, dict):
                continue

            try:
                records.append(
                    self._to_resume_record(item)
                )
            except Exception:
                continue

        return records

    def clear(self) -> None:
        """
        Kept only for compatibility with existing tests/code.

        Resume deletion is intentionally owned by Job Data Service.
        """
        return None


resume_repo = ResumeRepository()


class ResumeParserService:
    """
    Resume parser used by the AIML service.

    AIML performs parsing and skill extraction.
    Job Data Service permanently stores the resume and parsed results.
    """

    def __init__(
        self,
        upload_dir: Path = settings.UPLOAD_DIR,
        repo: ResumeRepository = resume_repo,
    ) -> None:
        self.upload_dir = upload_dir
        self.repo = repo

        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ------------------------------------------------------------------
    # Validation and text extraction
    # ------------------------------------------------------------------

    def validate_and_extract_text(
        self,
        filename: str,
        file_bytes: bytes,
    ) -> tuple[str, str]:
        if not file_bytes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded resume is empty.",
            )

        if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Resume file exceeds the 10 MB size limit.",
            )

        suffix = Path(filename).suffix.lower()

        if suffix not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "Unsupported resume format. "
                    "Allowed formats: PDF, DOCX, TXT."
                ),
            )

        try:
            if suffix == ".pdf":
                text = self._extract_pdf_text(file_bytes)

            elif suffix == ".docx":
                text = self._extract_docx_text(file_bytes)

            elif suffix == ".txt":
                text = file_bytes.decode(
                    "utf-8",
                    errors="ignore",
                )

            else:
                text = ""

        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unable to parse resume: {exc}",
            ) from exc

        text = text.strip()

        if not text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "No readable text could be extracted "
                    "from the uploaded resume."
                ),
            )

        return suffix, text

    @staticmethod
    def _extract_pdf_text(
        file_bytes: bytes,
    ) -> str:
        pages_text: list[str] = []

        try:
            with pdfplumber.open(
                io.BytesIO(file_bytes)
            ) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()

                    if page_text:
                        pages_text.append(page_text)

        except Exception:
            pages_text = []

        if pages_text:
            return "\n".join(pages_text)

        # Secondary PDF extraction fallback.
        reader = pypdf.PdfReader(
            io.BytesIO(file_bytes)
        )

        for page in reader.pages:
            try:
                page_text = page.extract_text()

                if page_text:
                    pages_text.append(page_text)
            except Exception:
                continue

        return "\n".join(pages_text)

    @staticmethod
    def _extract_docx_text(
        file_bytes: bytes,
    ) -> str:
        document = Document(
            io.BytesIO(file_bytes)
        )

        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]

        return "\n".join(paragraphs)

    # ------------------------------------------------------------------
    # Upload + persistence
    # ------------------------------------------------------------------

    async def parse_and_store_upload(
        self,
        upload_file: UploadFile,
        user_id: str | None = None,
    ) -> ResumeUploadResponse:
        filename = (
            upload_file.filename
            or "resume.pdf"
        )

        file_bytes = await upload_file.read()

        suffix, raw_text = (
            self.validate_and_extract_text(
                filename,
                file_bytes,
            )
        )

        parsed_skills = (
            skill_extractor.extract_skills(raw_text)
        )

        # --------------------------------------------------------------
        # Step 1: Store original resume in Job Data Service
        # --------------------------------------------------------------

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    "user_id is required for resume upload. "
                    "Provide user_id or X-User-ID."
                ),
            )

        try:
            job_data_response = self.repo._request(
                "POST",
                "/resumes/upload",
                user_id=user_id,
                files={
                    "file": (
                        filename,
                        file_bytes,
                        self._guess_content_type(suffix),
                    )
                },
                data={
                    "user_id": user_id,
                    "is_active_version": "true",
                },
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=str(exc),
            ) from exc

        if not isinstance(job_data_response, dict):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Job Data Service returned an invalid "
                    "resume upload response."
                ),
            )

        resume_id = str(
            job_data_response.get("id")
            or job_data_response.get("resume_id")
            or ""
        )

        if not resume_id:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Job Data Service did not return a resume ID."
                ),
            )

        # --------------------------------------------------------------
        # Step 2: Save AIML parsed results back into Job Data
        # --------------------------------------------------------------

        try:
            self.repo._request(
                "POST",
                f"/resumes/{resume_id}/parse",
                user_id=user_id,
                json={
                    "parsed_text": raw_text,
                    "extracted_skills": parsed_skills,
                },
            )
        except RuntimeError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=(
                    "Resume was stored, but parsed results "
                    f"could not be saved to Job Data Service: {exc}"
                ),
            ) from exc

        # --------------------------------------------------------------
        # Step 3: Return the canonical Job Data resume ID
        # --------------------------------------------------------------

        return ResumeUploadResponse(
            resume_id=resume_id,
            parsed_skills=parsed_skills,
        )

    @staticmethod
    def _guess_content_type(
        suffix: str,
    ) -> str:
        content_types = {
            ".pdf": "application/pdf",
            ".docx": (
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            ".txt": "text/plain",
        }

        return content_types.get(
            suffix,
            "application/octet-stream",
        )


resume_parser_service = ResumeParserService()