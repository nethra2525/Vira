"""
Resume Intelligence module.

Defines a provider-agnostic interface so a real LLM/NER-based parser can be
swapped in later (see `LiveResumeParser` stub). `MockResumeParser` gives
deterministic, explainable output with zero external dependencies so the
whole candidate flow works out of the box in dev/demo mode.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod

from app.core.config import get_settings

# A small seed taxonomy. In production this would be a proper skills table
# (see app.models.skills.Skill) looked up via fuzzy/semantic matching.
KNOWN_SKILLS = [
    "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "SQL",
    "PostgreSQL", "MongoDB", "Machine Learning", "Deep Learning", "Data Analysis",
    "Power BI", "Excel", "Tableau", "Java", "C++", "AWS", "Docker", "Kubernetes",
    "FastAPI", "Django", "Flask", "Git", "REST APIs", "HTML", "CSS", "Tailwind CSS",
    "Firebase", "Communication", "Project Management", "Figma", "UI/UX Design",
]


class BaseResumeParser(ABC):
    @abstractmethod
    def parse(self, raw_text: str) -> dict:
        """Return a structured candidate profile extracted from resume text."""


class MockResumeParser(BaseResumeParser):
    """Deterministic keyword + regex based extraction. No external API calls."""

    def parse(self, raw_text: str) -> dict:
        text = raw_text or ""

        name_match = re.search(r"(?m)^([A-Z][a-zA-Z]+(?:\s[A-Z][a-zA-Z]+){1,2})\s*$", text)
        detected_name = name_match.group(1) if name_match else None

        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text)
        phone_match = re.search(r"(\+?\d[\d\s-]{8,}\d)", text)

        found_skills = sorted(
            {s for s in KNOWN_SKILLS if re.search(rf"(?<![\w.+#-]){re.escape(s.lower())}(?![\w.+#-])", text.lower())}
        )

        education_lines = [
            line.strip() for line in text.splitlines()
            if any(kw in line.lower() for kw in ["b.e", "b.tech", "bachelor", "m.tech", "university", "college", "degree"])
        ][:5]

        experience_lines = [
            line.strip() for line in text.splitlines()
            if any(kw in line.lower() for kw in ["intern", "engineer", "developer", "experience", "worked", "led"])
        ][:5]

        return {
            "detected_name": detected_name,
            "detected_email": email_match.group(0) if email_match else None,
            "detected_phone": phone_match.group(0) if phone_match else None,
            "detected_skills": found_skills,
            "detected_education": education_lines,
            "detected_experience": experience_lines,
        }


class LiveResumeParser(BaseResumeParser):
    """
    Placeholder for a real provider (e.g. an LLM-based extraction call).
    Wire this up once LLM_API_KEY is set and AI_PROVIDER_MODE=live.
    """

    def parse(self, raw_text: str) -> dict:
        raise NotImplementedError(
            "Live resume parsing is not configured. Set LLM_API_KEY and implement "
            "LiveResumeParser.parse() to call your chosen provider."
        )


def get_resume_parser() -> BaseResumeParser:
    settings = get_settings()
    if settings.ai_provider_mode == "live" and settings.llm_api_key:
        return LiveResumeParser()
    return MockResumeParser()
