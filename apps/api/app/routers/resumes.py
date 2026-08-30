import json
import os
import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.resume_parser import get_resume_parser
from app.core.config import get_settings
from app.core.database import get_db
from app.core.deps import require_role
from app.models.skills import CandidateSkill, Resume, Skill
from app.models.user import CandidateProfile, User
from app.schemas.resumes import ParsedResumeOut

router = APIRouter(prefix="/resumes", tags=["resumes"])

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_FILE_SIZE_MB = 5


@router.post("/upload", response_model=ParsedResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()

    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only PDF, DOCX, or TXT resumes are supported.")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"File exceeds the {MAX_FILE_SIZE_MB}MB limit.")

    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    os.makedirs(settings.local_storage_dir, exist_ok=True)
    stored_name = f"{uuid.uuid4()}{ext}"
    stored_path = os.path.join(settings.local_storage_dir, stored_name)
    with open(stored_path, "wb") as f:
        f.write(contents)

    # Only .txt is decoded for real text in this mock pipeline; pdf/docx would
    # go through a real extraction library in production. We still accept and
    # store them, and run the mock parser against a decoded-best-effort string.
    try:
        raw_text = contents.decode("utf-8", errors="ignore") if ext == ".txt" else file.filename or ""
    except Exception:
        raw_text = file.filename or ""

    parser = get_resume_parser()
    parsed = parser.parse(raw_text)

    resume = Resume(
        candidate_id=profile.id,
        file_name=file.filename or stored_name,
        file_url=stored_path,
        parsed_status="parsed",
        raw_text=raw_text,
        parsed_json=json.dumps(parsed),
    )
    db.add(resume)
    await db.flush()

    # Sync detected skills into candidate_skills (normalized against the seed taxonomy).
    for skill_name in parsed.get("detected_skills", []):
        skill_result = await db.execute(select(Skill).where(Skill.name == skill_name))
        skill = skill_result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=skill_name, category="general")
            db.add(skill)
            await db.flush()

        existing_link = await db.execute(
            select(CandidateSkill).where(
                CandidateSkill.candidate_id == profile.id, CandidateSkill.skill_id == skill.id
            )
        )
        if not existing_link.scalar_one_or_none():
            db.add(CandidateSkill(candidate_id=profile.id, skill_id=skill.id, source="resume", proficiency=0.6))

    profile.profile_completion = min(100, profile.profile_completion + 25)
    await db.commit()

    return ParsedResumeOut(
        id=resume.id,
        file_name=resume.file_name,
        parsed_status=resume.parsed_status,
        detected_name=parsed.get("detected_name"),
        detected_skills=parsed.get("detected_skills", []),
        detected_education=parsed.get("detected_education", []),
        detected_experience=parsed.get("detected_experience", []),
    )


@router.get("/{resume_id}", response_model=ParsedResumeOut)
async def get_resume(
    resume_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    parsed = json.loads(resume.parsed_json or "{}")
    return ParsedResumeOut(
        id=resume.id,
        file_name=resume.file_name,
        parsed_status=resume.parsed_status,
        detected_name=parsed.get("detected_name"),
        detected_skills=parsed.get("detected_skills", []),
        detected_education=parsed.get("detected_education", []),
        detected_experience=parsed.get("detected_experience", []),
    )
