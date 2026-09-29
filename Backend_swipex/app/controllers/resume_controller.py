import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models import Resume, User
# Replace with your project's actual auth dependency
from app.auth import get_current_user 

router = APIRouter(tags=["Resumes"])

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB in bytes
ALLOWED_EXTENSIONS = {"pdf", "docx"}


def serialize_resume(resume: Resume) -> dict:
    return {
        "id": str(resume.id),
        "file_name": resume.file_name,
        "file_type": resume.file_type,
        "version_number": resume.version_number,
        "is_active_version": resume.is_active_version,
        "parsed_status": resume.parsed_status,
        "parsed_text": resume.parsed_text,
        "extracted_skills": resume.extracted_skills or [],
        "uploaded_at": resume.uploaded_at,
    }


@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # 1. Validate File Extension
    file_ext = file.filename.split(".")[-1].lower() if "." in file.filename else ""
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF and DOCX files are allowed.",
        )

    # 2. Validate File Size (10MB limit)
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds the maximum limit of 10MB.",
        )

    # 3. Calculate Auto-Incrementing Version Number for this user
    max_version = (
        db.query(func.max(Resume.version_number))
        .filter(Resume.user_id == current_user.id)
        .scalar()
    )
    new_version = (max_version or 0) + 1

    # 4. Deactivate previous active versions
    db.query(Resume).filter(
        Resume.user_id == current_user.id, 
        Resume.is_active_version == True
    ).update({"is_active_version": False})

    # 5. Create Resume Record
    new_resume = Resume(
        user_id=current_user.id,
        file_name=file.filename,
        file_type=file_ext,
        version_number=new_version,
        is_active_version=True,
        parsed_status="pending",
    )
    
    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "message": "Resume uploaded successfully",
        "resume": {
            "id": str(new_resume.id),
            "file_name": new_resume.file_name,
            "version_number": new_resume.version_number,
            "is_active_version": new_resume.is_active_version,
            "parsed_status": new_resume.parsed_status,
            "uploaded_at": new_resume.uploaded_at,
        },
    }


@router.get("", status_code=status.HTTP_200_OK)
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resumes = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.version_number.desc())
        .all()
    )
    return {"resumes": [serialize_resume(resume) for resume in resumes]}


@router.get("/{resume_id}", status_code=status.HTTP_200_OK)
def get_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()
    
    # Ownership Check: return 404 if not found or belongs to another user
    if not resume or resume.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found",
        )
        
    return serialize_resume(resume)


@router.patch("/{resume_id}/activate", status_code=status.HTTP_200_OK)
def activate_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    db.query(Resume).filter(Resume.user_id == current_user.id).update(
        {Resume.is_active_version: False}, synchronize_session=False
    )
    resume.is_active_version = True
    db.commit()
    db.refresh(resume)
    return serialize_resume(resume)


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resume(
    resume_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = db.query(Resume).filter(
        Resume.id == resume_id, Resume.user_id == current_user.id
    ).first()
    if resume is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")

    db.delete(resume)
    db.commit()
    return None