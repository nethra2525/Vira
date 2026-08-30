import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class AIRecommendation(Base, TimestampMixin):
    __tablename__ = "ai_recommendations"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    subject_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g. "application", "resume"
    subject_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=False)
    summary: Mapped[str] = mapped_column(Text, default="")
    explanation_json: Mapped[str] = mapped_column(Text, default="{}")


class SkillGapReport(Base, TimestampMixin):
    __tablename__ = "skill_gap_reports"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    job_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    missing_skills_json: Mapped[str] = mapped_column(Text, default="[]")


class GrowthPlan(Base, TimestampMixin):
    __tablename__ = "growth_plans"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    target_job_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    current_match: Mapped[float] = mapped_column(Float, default=0.0)
    previous_match: Mapped[float] = mapped_column(Float, default=0.0)
    steps_json: Mapped[str] = mapped_column(Text, default="[]")
    progress: Mapped[float] = mapped_column(Float, default=0.0)


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(80), default="general")
    message: Mapped[str] = mapped_column(Text, nullable=False)
    read_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)


class AuditLog(Base, TimestampMixin):
    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    actor_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False)
    entity_id: Mapped[uuid.UUID] = mapped_column(GUID(), nullable=True)
    metadata_json: Mapped[str] = mapped_column(Text, default="{}")
