import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.jobs import Job, JobSkill
from app.models.user import Company, RecruiterProfile, User
from app.models.skills import Skill
from app.schemas.jobs import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


async def _to_job_out(db: AsyncSession, job: Job) -> JobOut:
    company_result = await db.execute(select(Company).where(Company.id == job.company_id))
    company = company_result.scalar_one_or_none()

    js_result = await db.execute(
        select(JobSkill, Skill).join(Skill, JobSkill.skill_id == Skill.id).where(JobSkill.job_id == job.id)
    )
    rows = js_result.all()
    must_have = [s.name for js, s in rows if js.requirement_type == "must_have"]
    preferred = [s.name for js, s in rows if js.requirement_type == "preferred"]

    return JobOut(
        id=job.id,
        title=job.title,
        description=job.description,
        responsibilities=job.responsibilities,
        location=job.location,
        employment_type=job.employment_type,
        status=job.status,
        company_id=job.company_id,
        company_name=company.name if company else None,
        must_have_skills=must_have,
        preferred_skills=preferred,
    )


@router.get("", response_model=list[JobOut])
async def list_jobs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.status == "published"))
    jobs = result.scalars().all()
    return [await _to_job_out(db, j) for j in jobs]


@router.get("/{job_id}", response_model=JobOut)
async def get_job(job_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return await _to_job_out(db, job)


@router.post("", response_model=JobOut, status_code=201)
async def create_job(
    payload: JobCreate,
    user: User = Depends(require_role("recruiter")),
    db: AsyncSession = Depends(get_db),
):
    recruiter_result = await db.execute(select(RecruiterProfile).where(RecruiterProfile.user_id == user.id))
    recruiter = recruiter_result.scalar_one_or_none()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found.")

    job = Job(
        company_id=recruiter.company_id,
        title=payload.title,
        description=payload.description,
        responsibilities=payload.responsibilities,
        location=payload.location,
        employment_type=payload.employment_type,
        status=payload.status,
    )
    db.add(job)
    await db.flush()

    for req in payload.skills:
        skill_result = await db.execute(select(Skill).where(Skill.name == req.name))
        skill = skill_result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=req.name, category="general")
            db.add(skill)
            await db.flush()
        db.add(JobSkill(job_id=job.id, skill_id=skill.id, requirement_type=req.requirement_type))

    await db.commit()
    return await _to_job_out(db, job)


@router.patch("/{job_id}/publish", response_model=JobOut)
async def publish_job(
    job_id: uuid.UUID,
    user: User = Depends(require_role("recruiter")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Job).where(Job.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    job.status = "published"
    await db.commit()
    return await _to_job_out(db, job)


@router.get("/company/mine", response_model=list[JobOut])
async def list_my_company_jobs(
    user: User = Depends(require_role("recruiter")),
    db: AsyncSession = Depends(get_db),
):
    recruiter_result = await db.execute(select(RecruiterProfile).where(RecruiterProfile.user_id == user.id))
    recruiter = recruiter_result.scalar_one_or_none()
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter profile not found.")

    jobs_result = await db.execute(select(Job).where(Job.company_id == recruiter.company_id))
    jobs = jobs_result.scalars().all()
    return [await _to_job_out(db, j) for j in jobs]
