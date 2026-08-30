import uuid

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class Job(Base, TimestampMixin):
    __tablename__ = "jobs"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    company_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    responsibilities: Mapped[str] = mapped_column(Text, default="")
    location: Mapped[str] = mapped_column(String(255), default="Remote")
    employment_type: Mapped[str] = mapped_column(String(80), default="Full-time")
    status: Mapped[str] = mapped_column(Enum("draft", "published", "closed", name="job_status"), default="draft")

    company: Mapped["Company"] = relationship()


class JobSkill(Base, TimestampMixin):
    __tablename__ = "job_skills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("skills.id"), nullable=False)
    requirement_type: Mapped[str] = mapped_column(
        Enum("must_have", "preferred", name="requirement_type"), default="preferred"
    )

    skill: Mapped["Skill"] = relationship()


class Application(Base, TimestampMixin):
    __tablename__ = "applications"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    job_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("jobs.id"), nullable=False)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        Enum(
            "applied", "under_review", "assessment", "interview", "growth_path", "shortlisted", "rejected", "hired",
            name="application_status",
        ),
        default="applied",
    )
    match_score: Mapped[float] = mapped_column(Float, default=0.0)

    job: Mapped["Job"] = relationship()


# Imported here to avoid circular import at module load time
from app.models.user import Company  # noqa: E402
