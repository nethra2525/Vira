import json
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.assessment_engine import generate_assessment_questions, score_multiple_choice, score_scenario_response
from app.core.database import get_db
from app.core.deps import require_role
from app.models.assessments import Assessment, AssessmentAttempt, AssessmentResult, Question
from app.models.jobs import Job
from app.models.user import CandidateProfile, User
from app.schemas.resumes import (
    AssessmentQuestionOut,
    AssessmentResultOut,
    AssessmentStartOut,
    AssessmentSubmitRequest,
)

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/start", response_model=AssessmentStartOut)
async def start_assessment(
    assessment_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    profile_result = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
    profile = profile_result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Candidate profile not found.")

    assessment_result = await db.execute(select(Assessment).where(Assessment.id == assessment_id))
    assessment = assessment_result.scalar_one_or_none()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found.")

    questions_result = await db.execute(select(Question).where(Question.assessment_id == assessment_id))
    questions = questions_result.scalars().all()

    attempt = AssessmentAttempt(
        assessment_id=assessment_id,
        candidate_id=profile.id,
        status="in_progress",
        started_at=datetime.now(timezone.utc),
    )
    db.add(attempt)
    await db.commit()

    return AssessmentStartOut(
        attempt_id=attempt.id,
        assessment_id=assessment.id,
        round_type=assessment.round_type,
        duration_minutes=assessment.duration_minutes,
        questions=[
            AssessmentQuestionOut(
                id=q.id, question_type=q.question_type, prompt=q.prompt, options=json.loads(q.options_json or "[]")
            )
            for q in questions
        ],
    )


@router.post("/submit", response_model=AssessmentResultOut)
async def submit_assessment(
    payload: AssessmentSubmitRequest,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    attempt_result = await db.execute(select(AssessmentAttempt).where(AssessmentAttempt.id == payload.attempt_id))
    attempt = attempt_result.scalar_one_or_none()
    if not attempt:
        raise HTTPException(status_code=404, detail="Assessment attempt not found.")

    assessment_result = await db.execute(select(Assessment).where(Assessment.id == attempt.assessment_id))
    assessment = assessment_result.scalar_one_or_none()

    questions_result = await db.execute(select(Question).where(Question.assessment_id == attempt.assessment_id))
    questions = {str(q.id): q for q in questions_result.scalars().all()}

    if assessment and assessment.round_type == "scenario":
        combined_text = " ".join(a.answer_text for a in payload.answers)
        scored = score_scenario_response(combined_text)
    else:
        q_list = [
            {"correct_option": questions[str(a.question_id)].correct_option}
            for a in payload.answers
            if str(a.question_id) in questions
        ]
        a_list = [{"answer_text": a.answer_text} for a in payload.answers]
        scored = score_multiple_choice(a_list, q_list)

    attempt.status = "submitted"
    attempt.submitted_at = datetime.now(timezone.utc)

    result_row = AssessmentResult(
        attempt_id=attempt.id,
        score=scored["score"],
        breakdown_json=json.dumps(scored["breakdown"]),
        feedback_text=scored["feedback"],
    )
    db.add(result_row)
    await db.commit()

    return AssessmentResultOut(score=scored["score"], breakdown=scored["breakdown"], feedback=scored["feedback"])
