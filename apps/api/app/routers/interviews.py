import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.interview_assistant import build_interview_summary, next_question
from app.core.database import get_db
from app.core.deps import require_role
from app.models.interviews import InterviewResponse, InterviewSession
from app.models.jobs import Application
from app.models.user import User

router = APIRouter(prefix="/interviews", tags=["interviews"])


class RespondRequest(BaseModel):
    transcript: str


@router.post("/start")
async def start_interview(
    application_id: uuid.UUID,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    app_result = await db.execute(select(Application).where(Application.id == application_id))
    application = app_result.scalar_one_or_none()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    session = InterviewSession(
        application_id=application_id, status="in_progress", started_at=datetime.now(timezone.utc)
    )
    db.add(session)
    await db.commit()

    first_question = next_question(0)
    return {"session_id": session.id, "question": first_question, "question_index": 0}


@router.post("/{session_id}/respond")
async def respond_to_question(
    session_id: uuid.UUID,
    payload: RespondRequest,
    prompt: str,
    question_index: int,
    user: User = Depends(require_role("candidate")),
    db: AsyncSession = Depends(get_db),
):
    session_result = await db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
    session = session_result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    db.add(InterviewResponse(session_id=session_id, question_text=prompt, transcript=payload.transcript))
    await db.commit()

    upcoming = next_question(question_index + 1, previous_answer=payload.transcript)
    if upcoming is None:
        responses_result = await db.execute(
            select(InterviewResponse).where(InterviewResponse.session_id == session_id)
        )
        responses = [{"transcript": r.transcript} for r in responses_result.scalars().all()]
        summary = build_interview_summary(responses)

        session.status = "completed"
        session.ended_at = datetime.now(timezone.utc)
        session.summary_text = summary
        await db.commit()

        return {"completed": True, "summary": summary}

    return {"completed": False, "question": upcoming, "question_index": question_index + 1}
