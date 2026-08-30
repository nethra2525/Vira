import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import require_role
from app.models.jobs import Application, Job
from app.models.skills import CandidateSkill
from app.models.user import CandidateProfile, User

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("/me")
async def get_my_profile(
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    skills_result = await db.execute(
        select(CandidateSkill).where(CandidateSkill.candidate_id == profile.id)
    )
    skills = skills_result.scalars().all()

    return {
        "id": profile.id,
        "full_name": user.full_name,
        "email": user.email,
        "headline": profile.headline,
        "location": profile.location,
        "profile_completion": profile.profile_completion,
        "skill_count": len(skills),
    }


@router.get("/me/dashboard")
async def get_dashboard(
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    apps_result = await db.execute(
        select(Application, Job).join(Job, Application.job_id == Job.id).where(Application.candidate_id == profile.id)
    )
    rows = apps_result.all()

    applications = [
        {
            "id": app.id,
            "job_id": job.id,
            "job_title": job.title,
            "status": app.status,
            "match_score": app.match_score,
        }
        for app, job in rows
    ]

    interviews_scheduled = sum(1 for a in applications if a["status"] == "interview")
    avg_match = round(sum(a["match_score"] for a in applications) / len(applications), 1) if applications else 0.0

    return {
        "welcome_name": user.full_name.split(" ")[0],
        "profile_completion": profile.profile_completion,
        "career_overview": {
            "applications": len(applications),
            "interviews_scheduled": interviews_scheduled,
            "average_match_score": avg_match,
        },
        "applications": applications,
    }
