import io
import uuid
from datetime import UTC, datetime
from pathlib import Path

import pdfplumber
import pypdf
from fastapi import HTTPException, UploadFile, status

from backend.app.core.config import settings
from backend.app.models.schemas import ResumeRecord, ResumeUploadResponse
from backend.app.services.skill_extractor import skill_extractor


class ResumeRepository:
    def __init__(self):
        self._resumes: dict[str, ResumeRecord] = {}
        self._user_resumes: dict[str, list[str]] = {}

    def save(self, record: ResumeRecord) -> None:
        self._resumes[record.resume_id] = record
        if record.user_id:
            if record.user_id not in self._user_resumes:
                self._user_resumes[record.user_id] = []
            self._user_resumes[record.user_id].append(record.resume_id)

    def get_by_id(self, resume_id: str) -> ResumeRecord | None:
        return self._resumes.get(resume_id)

    def get_latest_by_user_id(self, user_id: str) -> ResumeRecord | None:
        resume_ids = self._user_resumes.get(user_id, [])
        if not resume_ids:
            return None
        latest_id = resume_ids[-1]
        return self._resumes.get(latest_id)

    def list_all(self) -> list[ResumeRecord]:
        return list(self._resumes.values())

    def clear(self) -> None:
        self._resumes.clear()
        self._user_resumes.clear()


resume_repo = ResumeRepository()


class ResumeParserService:
    def __init__(
        self, repo: ResumeRepository = resume_repo, upload_dir: Path = settings.UPLOAD_DIR
    ):
        self.repo = repo
        self.upload_dir = upload_dir
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        text_content = []
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if len(pdf.pages) == 0:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="The uploaded PDF file contains no pages.",
                    )
                for page in pdf.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content.append(extracted)
        except HTTPException:
            raise
        except Exception as e:
            try:
                reader = pypdf.PdfReader(io.BytesIO(file_bytes))
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text_content.append(extracted)
            except Exception as fallback_err:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unable to parse PDF content: {e!s} / {fallback_err!s}",
                )

        full_text = "\n".join(text_content).strip()
        return full_text

    def extract_text_from_docx(self, file_bytes: bytes) -> str:
        try:
            import docx

            doc = docx.Document(io.BytesIO(file_bytes))
            text_lines = [p.text for p in doc.paragraphs if p.text and p.text.strip()]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        if cell.text and cell.text.strip():
                            text_lines.append(cell.text.strip())
            return "\n".join(text_lines).strip()
        except Exception:
            try:
                import xml.etree.ElementTree as ET
                import zipfile

                with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
                    xml_content = z.read("word/document.xml")
                    tree = ET.fromstring(xml_content)
                    texts = [
                        node.text for node in tree.iter() if node.tag.endswith("t") and node.text
                    ]
                    return " ".join(texts).strip()
            except Exception as fallback_err:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Unable to parse DOCX content: {fallback_err!s}",
                )

    def extract_text_from_txt(self, file_bytes: bytes) -> str:
        for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252", "ascii"]:
            try:
                return file_bytes.decode(encoding).strip()
            except (UnicodeDecodeError, AttributeError):
                continue

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Unable to decode text file. Ensure it is encoded in UTF-8 or ASCII.",
        )

    def validate_and_extract_text(self, filename: str, file_bytes: bytes) -> tuple[str, str]:
        if not file_bytes or len(file_bytes.strip()) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The uploaded file is empty. Please upload a valid resume.",
            )

        if len(file_bytes) > settings.MAX_FILE_SIZE_BYTES:
            max_mb = settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum allowed size of {max_mb} MB.",
            )

        ext = Path(filename).suffix.lower() if filename else ""
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '{ext}'. Allowed formats: {list(settings.ALLOWED_EXTENSIONS)}",
            )

        if ext == ".pdf":
            raw_text = self.extract_text_from_pdf(file_bytes)
        elif ext == ".docx":
            raw_text = self.extract_text_from_docx(file_bytes)
        elif ext == ".txt":
            raw_text = self.extract_text_from_txt(file_bytes)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Unsupported format: {ext}"
            )

        if not raw_text or not raw_text.strip():
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No readable text could be extracted from the uploaded resume.",
            )

        return ext, raw_text

    async def parse_and_store_upload(
        self, upload_file: UploadFile, user_id: str | None = None
    ) -> ResumeUploadResponse:
        filename = upload_file.filename or "unknown_resume.pdf"
        file_bytes = await upload_file.read()

        ext, raw_text = self.validate_and_extract_text(filename, file_bytes)

        resume_id = f"res_{uuid.uuid4().hex[:12]}"

        safe_filename = f"{resume_id}{ext}"
        save_path = self.upload_dir / safe_filename
        with open(save_path, "wb") as f:
            f.write(file_bytes)

        parsed_skills = skill_extractor.extract_skills(raw_text)

        record = ResumeRecord(
            resume_id=resume_id,
            user_id=user_id,
            original_filename=filename,
            file_path=str(save_path),
            file_type=ext,
            raw_text=raw_text,
            parsed_skills=parsed_skills,
            created_at=datetime.now(UTC),
        )
        self.repo.save(record)

        return ResumeUploadResponse(resume_id=resume_id, parsed_skills=parsed_skills)


resume_parser_service = ResumeParserService()
