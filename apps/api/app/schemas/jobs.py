import uuid

from pydantic import BaseModel


class SkillRequirement(BaseModel):
    name: str
    requirement_type: str = "preferred"  # "must_have" | "preferred"


class JobCreate(BaseModel):
    title: str
    description: str
    responsibilities: str = ""
    location: str = "Remote"
    employment_type: str = "Full-time"
    skills: list[SkillRequirement] = []
    status: str = "draft"


class JobOut(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    responsibilities: str
    location: str
    employment_type: str
    status: str
    company_id: uuid.UUID
    company_name: str | None = None
    must_have_skills: list[str] = []
    preferred_skills: list[str] = []

    class Config:
        from_attributes = True


class ApplicationOut(BaseModel):
    id: uuid.UUID
    job_id: uuid.UUID
    job_title: str
    status: str
    match_score: float

    class Config:
        from_attributes = True
