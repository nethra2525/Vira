import uuid

from sqlalchemy import Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import GUID, TimestampMixin, new_uuid


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(
        Enum("candidate", "recruiter", "admin", name="user_role"), nullable=False, default="candidate"
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    candidate_profile: Mapped["CandidateProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    recruiter_profile: Mapped["RecruiterProfile"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan"
    )


class CandidateProfile(Base, TimestampMixin):
    __tablename__ = "candidate_profiles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), unique=True, nullable=False)
    headline: Mapped[str] = mapped_column(String(255), default="")
    location: Mapped[str] = mapped_column(String(255), default="")
    profile_completion: Mapped[int] = mapped_column(Integer, default=10)

    user: Mapped["User"] = relationship(back_populates="candidate_profile")


class Company(Base, TimestampMixin):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    industry: Mapped[str] = mapped_column(String(255), default="")
    verified_status: Mapped[str] = mapped_column(
        Enum("pending", "verified", "rejected", name="company_verified_status"), default="pending"
    )


class RecruiterProfile(Base, TimestampMixin):
    __tablename__ = "recruiter_profiles"

    id: Mapped[uuid.UUID] = mapped_column(GUID(), primary_key=True, default=new_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("users.id"), unique=True, nullable=False)
    company_id: Mapped[uuid.UUID] = mapped_column(GUID(), ForeignKey("companies.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), default="")

    user: Mapped["User"] = relationship(back_populates="recruiter_profile")
    company: Mapped["Company"] = relationship()
