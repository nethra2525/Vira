import uuid

from pydantic import BaseModel


class ParsedResumeOut(BaseModel):
    id: uuid.UUID
    file_name: str
    parsed_status: str
    detected_name: str | None = None
    detected_skills: list[str] = []
    detected_education: list[str] = []
    detected_experience: list[str] = []

    class Config:
        from_attributes = True


class AssessmentQuestionOut(BaseModel):
    id: uuid.UUID
    question_type: str
    prompt: str
    options: list[str] = []


class AssessmentStartOut(BaseModel):
    attempt_id: uuid.UUID
    assessment_id: uuid.UUID
    round_type: str
    duration_minutes: int
    questions: list[AssessmentQuestionOut]


class AssessmentAnswer(BaseModel):
    question_id: uuid.UUID
    answer_text: str


class AssessmentSubmitRequest(BaseModel):
    attempt_id: uuid.UUID
    answers: list[AssessmentAnswer]


class AssessmentResultOut(BaseModel):
    score: float
    breakdown: dict
    feedback: str
