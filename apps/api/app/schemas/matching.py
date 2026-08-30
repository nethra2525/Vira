import uuid

from pydantic import BaseModel


class MatchBreakdown(BaseModel):
    skills_match: float
    experience_relevance: float
    project_relevance: float
    assessment_readiness: float


class MatchResult(BaseModel):
    application_id: uuid.UUID | None = None
    job_id: uuid.UUID
    candidate_id: uuid.UUID
    overall_score: float
    breakdown: MatchBreakdown
    matched_skills: list[str]
    missing_must_have: list[str]
    missing_preferred: list[str]
    explanation: str
    disclaimer: str = (
        "VIRA provides AI-assisted insights to support recruitment decisions. "
        "Final hiring decisions remain with authorized human reviewers."
    )


class GrowthPathStep(BaseModel):
    order: int
    action: str
    related_skill: str | None = None


class GrowthPathOut(BaseModel):
    candidate_id: uuid.UUID
    target_job_id: uuid.UUID
    current_match: float
    previous_match: float | None = None
    strengths: list[str]
    skills_to_improve: list[str]
    steps: list[GrowthPathStep]
    progress: float
