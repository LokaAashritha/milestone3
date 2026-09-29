import os
import uuid
import hashlib
from pathlib import Path
from typing import Tuple
from fastapi import HTTPException, status
from app.core.config import settings

# Allowed extensions and MIME types
ALLOWED_EXTENSIONS = {"pdf", "docx"}
MAX_FILE_SIZE_BYTES = 10 * 1024 * 1024  # 10 MB limit (FR-01 / Contract requirement)


class FileStorageManager:
    """
    Local file storage manager for uploaded resumes in the development/local environment.
    Provides path sanitization, version/UUID directory isolation, SHA256 integrity checksums,
    and size/format validation.
    """

    def __init__(self, base_upload_dir: str = "./uploads/resumes"):
        self.base_upload_dir = Path(base_upload_dir)
        self.base_upload_dir.mkdir(parents=True, exist_ok=True)

    def validate_file(self, filename: str, content: bytes) -> str:
        """Validate file format and maximum size. Raises HTTP 400 or 413."""
        if not filename or "." not in filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file name: missing extension. Only PDF and DOCX files are allowed."
            )
        
        ext = filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file format '.{ext}'. Only PDF and DOCX files are supported."
            )

        file_size = len(content)
        if file_size > MAX_FILE_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE if hasattr(status, "HTTP_413_CONTENT_TOO_LARGE") else 413,
                detail=f"File size ({file_size / (1024 * 1024):.2f}MB) exceeds maximum limit of 10MB."
            )
        
        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes)."
            )

        return ext

    def save_resume_file(
        self, user_id: str, original_filename: str, content: bytes, version_number: int
    ) -> Tuple[str, str, int, str]:
        """
        Saves resume file to isolated user storage directory.
        Returns: (saved_file_path, file_type, file_size, sha256_hash)
        """
        ext = self.validate_file(original_filename, content)
        
        user_dir = self.base_upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)

        # Secure unique filename incorporating version and random uuid segment
        safe_base = Path(original_filename).stem.replace(" ", "_")[:50]
        unique_filename = f"v{version_number}_{uuid.uuid4().hex[:8]}_{safe_base}.{ext}"
        target_path = user_dir / unique_filename

        with open(target_path, "wb") as f:
            f.write(content)

        file_size = len(content)
        sha256_hash = hashlib.sha256(content).hexdigest()

        return str(target_path), ext, file_size, sha256_hash

    def read_resume_file(self, file_path: str) -> bytes:
        """Reads resume file bytes from disk."""
        path = Path(file_path)
        if not path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume file not found on disk storage."
            )
        with open(path, "rb") as f:
            return f.read()

    def delete_resume_file(self, file_path: str) -> bool:
        """Safely removes file from storage."""
        try:
            path = Path(file_path)
            if path.exists():
                path.unlink()
                return True
        except Exception:
            pass
        return False


# Singleton instance for application use
storage_manager = FileStorageManager()
