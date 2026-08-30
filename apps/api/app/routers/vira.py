from pydantic import BaseModel

from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/vira", tags=["vira"])


class ChatRequest(BaseModel):
    message: str
    context: str | None = None  # e.g. "job_detail", "growth_path", "dashboard"


class ChatResponse(BaseModel):
    reply: str
    disclaimer: str = (
        "VIRA provides AI-assisted guidance, not a final hiring decision. "
        "Always review important details with a human recruiter."
    )


# A small set of canned, context-aware responses. This keeps the assistant
# genuinely useful in demo/dev mode with zero external LLM dependency; swap
# in a real provider call here once AI_PROVIDER_MODE=live.
def _mock_reply(message: str, context: str | None) -> str:
    lowered = message.lower()
    if "why" in lowered and "match" in lowered:
        return (
            "Your match score weighs four things: skills overlap (45%), experience relevance (20%), "
            "project relevance (15%), and assessment readiness (20%). Check the 'Why this match score?' "
            "panel on the job page for the exact breakdown."
        )
    if "improve" in lowered or "growth" in lowered:
        return (
            "Your Growth Path lists the specific skills to focus on next, in priority order. "
            "Completing the suggested assessment is usually the fastest way to move your match score."
        )
    if "interview" in lowered:
        return (
            "For VIRA CALL, take your time -- there's no penalty for pausing before answering. "
            "Each question is scored against a transparent rubric: clarity, relevance, and problem-solving approach."
        )
    return (
        "I can help explain match scores, skill gaps, growth plans, or what to expect in an assessment. "
        "What would you like to know?"
    )


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, user: User = Depends(get_current_user)):
    return ChatResponse(reply=_mock_reply(payload.message, payload.context))
