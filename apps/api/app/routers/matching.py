import json
import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.growth_path import build_growth_path
from app.ai.match_engine import MatchInputs, compute_match
from app.core.database import get_db
from app.core.deps import require_role
from app.models.ai_and_system import AIRecommendation, GrowthPlan
from app.models.assessments import AssessmentResult, AssessmentAttempt
from app.models.jobs import Application, Job, JobSkill
from app.models.skills import CandidateSkill, Skill
from app.models.user import CandidateProfile, User
from app.schemas.matching import GrowthPathOut, MatchBreakdown, MatchResult

router = APIRouter(prefix="/matching", tags=["matching"])


async def _candidate_skill_names(db: AsyncSession, candidate_id: uuid.UUID) -> list[str]:
    result = await db.execute(
        select(Skill.name).join(CandidateSkill, CandidateSkill.skill_id == Skill.id).where(
            CandidateSkill.candidate_id == candidate_id
        )
    )
    return [row[0] for row in result.all()]


async def _job_skill_names(db: AsyncSession, job_id: uuid.UUID) -> tuple[list[str], list[str]]:
    result = await db.execute(
        select(JobSkill, Skill).join(Skill, JobSkill.skill_id == Skill.id).where(JobSkill.job_id == job_id)
    )
    rows = result.all()
    must = [s.name for js, s in rows if js.requirement_type == "must_have"]
    preferred = [s.name for js, s in rows if js.requirement_type == "preferred"]
    return must, preferred


async def _avg_assessment_score(db: AsyncSession, candidate_id: uuid.UUID) -> float | None:
    result = await db.execute(
        select(AssessmentResult.score)
        .join(AssessmentAttempt, AssessmentResult.attempt_id == AssessmentAttempt.id)
        .where(AssessmentAttempt.candidate_id == candidate_id)
    )
    scores = [row[0] for row in result.all()]
    return round(sum(scores) / len(scores), 1) if scores else None


@router.post("/analyze", response_model=MatchResult)
async def analyze_match(
    job_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    job_result = await db.execute(select(Job).where(Job.id == job_id))
    job = job_result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")

    candidate_skills = await _candidate_skill_names(db, profile.id)
    must_have, preferred = await _job_skill_names(db, job_id)
    avg_score = await _avg_assessment_score(db, profile.id)

    inputs = MatchInputs(
        candidate_skills=candidate_skills,
        must_have_skills=must_have,
        preferred_skills=preferred,
        candidate_experience_years=1.0,
        job_seniority_hint=0.5,
        candidate_project_keywords=candidate_skills,
        job_keywords=must_have + preferred,
        assessment_avg_score=avg_score,
    )
    result = compute_match(inputs)

    db.add(
        AIRecommendation(
            subject_type="job_match",
            subject_id=job_id,
            summary=result["explanation"],
            explanation_json=json.dumps(result),
        )
    )
    await db.commit()

    return MatchResult(
        job_id=job_id,
        candidate_id=profile.id,
        overall_score=result["overall_score"],
        breakdown=MatchBreakdown(**result["breakdown"]),
        matched_skills=result["matched_skills"],
        missing_must_have=result["missing_must_have"],
        missing_preferred=result["missing_preferred"],
        explanation=result["explanation"],
    )


@router.get("/{job_id}/growth-path", response_model=GrowthPathOut)
async def get_growth_path(
    job_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    candidate_skills = await _candidate_skill_names(db, profile.id)
    must_have, preferred = await _job_skill_names(db, job_id)
    avg_score = await _avg_assessment_score(db, profile.id)

    inputs = MatchInputs(
        candidate_skills=candidate_skills,
        must_have_skills=must_have,
        preferred_skills=preferred,
        candidate_experience_years=1.0,
        job_seniority_hint=0.5,
        candidate_project_keywords=candidate_skills,
        job_keywords=must_have + preferred,
        assessment_avg_score=avg_score,
    )
    match = compute_match(inputs)

    existing_plan_result = await db.execute(
        select(GrowthPlan).where(GrowthPlan.candidate_id == profile.id, GrowthPlan.target_job_id == job_id)
    )
    existing_plan = existing_plan_result.scalar_one_or_none()
    previous_match = existing_plan.current_match if existing_plan else None

    growth = build_growth_path(
        matched_skills=match["matched_skills"],
        missing_must_have=match["missing_must_have"],
        missing_preferred=match["missing_preferred"],
        current_match=match["overall_score"],
        previous_match=previous_match,
    )

    if existing_plan:
        existing_plan.previous_match = existing_plan.current_match
        existing_plan.current_match = match["overall_score"]
        existing_plan.steps_json = json.dumps(growth["steps"])
        existing_plan.progress = growth["progress"]
    else:
        db.add(
            GrowthPlan(
                candidate_id=profile.id,
                target_job_id=job_id,
                current_match=match["overall_score"],
                previous_match=0.0,
                steps_json=json.dumps(growth["steps"]),
                progress=0.0,
            )
        )
    await db.commit()

    return GrowthPathOut(
        candidate_id=profile.id,
        target_job_id=job_id,
        current_match=growth["current_match"],
        previous_match=growth["previous_match"],
        strengths=growth["strengths"],
        skills_to_improve=growth["skills_to_improve"],
        steps=growth["steps"],
        progress=growth["progress"],
    )


@router.post("/{job_id}/apply")
async def apply_to_job(
    job_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    candidate_skills = await _candidate_skill_names(db, profile.id)
    must_have, preferred = await _job_skill_names(db, job_id)
    avg_score = await _avg_assessment_score(db, profile.id)
    inputs = MatchInputs(
        candidate_skills=candidate_skills,
        must_have_skills=must_have,
        preferred_skills=preferred,
        candidate_experience_years=1.0,
        job_seniority_hint=0.5,
        candidate_project_keywords=candidate_skills,
        job_keywords=must_have + preferred,
        assessment_avg_score=avg_score,
    )
    result = compute_match(inputs)

    application = Application(
        job_id=job_id,
        candidate_id=profile.id,
        status="applied",
        match_score=result["overall_score"],
    )
    db.add(application)
    await db.commit()
    return {"application_id": application.id, "status": application.status, "match_score": application.match_score}
