import uuid

from sqlalchemy import Enum, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class Skill(Base, TimestampMixin):
    __tablename__ = "skills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(120), default="general")


class CandidateSkill(Base, TimestampMixin):
    __tablename__ = "candidate_skills"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    skill_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("skills.id"), nullable=False)
    source: Mapped[str] = mapped_column(
        Enum("resume", "assessment", "manual", name="skill_source"), default="manual"
    )
    proficiency: Mapped[float] = mapped_column(Float, default=0.5)  # 0.0 - 1.0

    skill: Mapped["Skill"] = relationship()


class Resume(Base, TimestampMixin):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    candidate_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("candidate_profiles.id"), nullable=False)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    parsed_status: Mapped[str] = mapped_column(
        Enum("pending", "parsed", "failed", name="resume_parsed_status"), default="pending"
    )
    raw_text: Mapped[str] = mapped_column(Text, default="")
    parsed_json: Mapped[str] = mapped_column(Text, default="{}")  # structured extraction, stored as JSON text
