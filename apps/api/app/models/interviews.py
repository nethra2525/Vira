import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class InterviewSession(Base, TimestampMixin):
    __tablename__ = "interview_sessions"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    application_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("applications.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum("not_started", "in_progress", "completed", name="interview_status"), default="not_started"
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    ended_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    summary_text: Mapped[str] = mapped_column(Text, default="")


class InterviewResponse(Base, TimestampMixin):
    __tablename__ = "interview_responses"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("interview_sessions.id"), nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    transcript: Mapped[str] = mapped_column(Text, default="")
    is_follow_up: Mapped[bool] = mapped_column(default=False)
