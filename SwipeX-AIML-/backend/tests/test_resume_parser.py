import asyncio
import io
import zipfile

import pytest
from fastapi import HTTPException, UploadFile

from backend.app.services.resume_parser import ResumeParserService, resume_repo


def create_dummy_docx_bytes() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        xml_content = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
            "<w:body><w:p><w:r><w:t>Alex Rivera Python FastAPI Docker Developer Resume</w:t></w:r></w:p></w:body>"
            "</w:document>"
        )
        z.writestr("word/document.xml", xml_content)
    return buf.getvalue()


def test_extract_text_from_txt(sample_txt_frontend):
    parser = ResumeParserService()
    file_bytes = sample_txt_frontend.read_bytes()
    ext, text = parser.validate_and_extract_text("sarah_resume.txt", file_bytes)
    assert ext == ".txt"
    assert "Sarah Chen" in text
    assert "React" in text
    assert "Tailwind CSS" in text


def test_extract_text_from_pdf(sample_pdf_backend):
    parser = ResumeParserService()
    file_bytes = sample_pdf_backend.read_bytes()
    ext, text = parser.validate_and_extract_text("alex_resume.pdf", file_bytes)
    assert ext == ".pdf"
    assert "Alex Rivera" in text
    assert "FastAPI" in text
    assert "PostgreSQL" in text


def test_extract_text_from_docx():
    parser = ResumeParserService()
    docx_bytes = create_dummy_docx_bytes()
    ext, text = parser.validate_and_extract_text("alex_resume.docx", docx_bytes)
    assert ext == ".docx"
    assert "Alex Rivera" in text
    assert "Python" in text
    assert "FastAPI" in text


def test_empty_file_upload_error():
    parser = ResumeParserService()
    with pytest.raises(HTTPException) as exc_info:
        parser.validate_and_extract_text("empty.txt", b"")
    assert exc_info.value.status_code == 400
    assert "empty" in exc_info.value.detail.lower()


def test_unsupported_file_extension():
    parser = ResumeParserService()
    with pytest.raises(HTTPException) as exc_info:
        parser.validate_and_extract_text("resume.exe", b"dummy content here")
    assert exc_info.value.status_code == 400
    assert "unsupported" in exc_info.value.detail.lower()


def test_corrupted_pdf_handling():
    parser = ResumeParserService()
    corrupted_bytes = b"%PDF-1.4\ncorrupted header and body without xref\n%%EOF"
    with pytest.raises(HTTPException) as exc_info:
        parser.validate_and_extract_text("corrupt.pdf", corrupted_bytes)
    assert exc_info.value.status_code in [400, 422]


def test_parse_and_store_upload(sample_pdf_backend):
    parser = ResumeParserService()
    file_bytes = sample_pdf_backend.read_bytes()
    upload_file = UploadFile(filename="alex_backend.pdf", file=io.BytesIO(file_bytes))
    res = asyncio.run(parser.parse_and_store_upload(upload_file, user_id="user_123"))
    assert res.resume_id.startswith("res_")
    assert "Python" in res.parsed_skills
    assert "FastAPI" in res.parsed_skills
    assert "Docker" in res.parsed_skills

    record = resume_repo.get_by_id(res.resume_id)
    assert record is not None
    assert record.user_id == "user_123"
    assert record.original_filename == "alex_backend.pdf"

    latest = resume_repo.get_latest_by_user_id("user_123")
    assert latest.resume_id == res.resume_id
