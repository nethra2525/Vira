import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    round_type: Mapped[str] = mapped_column(
        Enum("aptitude", "technical", "scenario", name="round_type"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)


class Question(Base, TimestampMixin):
    __tablename__ = "questions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    assessment_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("assessments.id"), nullable=False)
    question_type: Mapped[str] = mapped_column(
        Enum("multiple_choice", "scenario", name="question_type"), default="multiple_choice"
    )
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[str] = mapped_column(Text, default="[]")
    correct_option: Mapped[str] = mapped_column(String(255), default="")
    rubric_json: Mapped[str] = mapped_column(Text, default="{}")


class AssessmentAttempt(Base, TimestampMixin):
    __tablename__ = "assessment_attempts"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    assessment_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("assessments.id"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("in_progress", "submitted", name="attempt_status"), default="in_progress"
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class AssessmentResult(Base, TimestampMixin):
    __tablename__ = "assessment_results"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    attempt_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("assessment_attempts.id"), nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0)
    breakdown_json: Mapped[str] = mapped_column(Text, default="{}")
    feedback_text: Mapped[str] = mapped_column(Text, default="")
