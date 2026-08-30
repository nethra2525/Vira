"""
AI Job Matching Engine.

Combines structured skill overlap with lightweight semantic-ish heuristics to
produce a transparent, explainable match score. Every score ships with a
breakdown and plain-language explanation -- never a bare number.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MatchInputs:
    candidate_skills: list[str]
    must_have_skills: list[str]
    preferred_skills: list[str]
    candidate_experience_years: float
    job_seniority_hint: float  # 0.0 (entry) - 1.0 (senior), rough proxy
    candidate_project_keywords: list[str]
    job_keywords: list[str]
    assessment_avg_score: float | None  # 0-100, None if not yet attempted


def _normalize(term: str) -> str:
    return term.strip().lower()


def compute_match(inputs: MatchInputs) -> dict:
    # Preserve original casing (e.g. "SQL", "Power BI") by mapping normalized -> display name.
    display_name: dict[str, str] = {}
    for s in inputs.candidate_skills + inputs.must_have_skills + inputs.preferred_skills:
        display_name.setdefault(_normalize(s), s.strip())

    candidate_set = {_normalize(s) for s in inputs.candidate_skills}
    must_have_set = {_normalize(s) for s in inputs.must_have_skills}
    preferred_set = {_normalize(s) for s in inputs.preferred_skills}

    matched_must = must_have_set & candidate_set
    matched_preferred = preferred_set & candidate_set
    missing_must = must_have_set - candidate_set
    missing_preferred = preferred_set - candidate_set

    total_required = len(must_have_set) + len(preferred_set)
    if total_required > 0:
        # Must-have skills are weighted more heavily than preferred ones.
        skills_match = (
            (len(matched_must) * 2 + len(matched_preferred) * 1)
            / (len(must_have_set) * 2 + len(preferred_set) * 1)
            * 100
        ) if (len(must_have_set) * 2 + len(preferred_set) * 1) > 0 else 0.0
    else:
        skills_match = 100.0 if candidate_set else 0.0

    experience_relevance = min(100.0, (inputs.candidate_experience_years / max(inputs.job_seniority_hint * 4, 1)) * 100)
    experience_relevance = max(20.0, experience_relevance)  # a floor so new grads aren't zeroed out

    project_overlap = {_normalize(k) for k in inputs.candidate_project_keywords} & {
        _normalize(k) for k in inputs.job_keywords
    }
    project_relevance = min(100.0, (len(project_overlap) / max(len(inputs.job_keywords), 1)) * 100 + 30)

    assessment_readiness = inputs.assessment_avg_score if inputs.assessment_avg_score is not None else 60.0

    overall = round(
        skills_match * 0.45
        + experience_relevance * 0.20
        + project_relevance * 0.15
        + assessment_readiness * 0.20,
        1,
    )

    explanation_parts = []
    if matched_must:
        explanation_parts.append(
            f"Demonstrates {len(matched_must)} of {len(must_have_set)} must-have skills "
            f"({', '.join(sorted(display_name.get(s, s) for s in matched_must))})."
        )
    if matched_preferred:
        explanation_parts.append(f"Also shows {len(matched_preferred)} preferred skill(s).")
    if project_overlap:
        explanation_parts.append("Relevant project experience aligns with this role's focus areas.")
    if inputs.assessment_avg_score is not None:
        explanation_parts.append(f"Assessment performance averaged {inputs.assessment_avg_score:.0f}%.")
    if not explanation_parts:
        explanation_parts.append("Limited overlap detected between the candidate profile and this role's requirements.")

    explanation = " ".join(explanation_parts)

    return {
        "overall_score": overall,
        "breakdown": {
            "skills_match": round(skills_match, 1),
            "experience_relevance": round(experience_relevance, 1),
            "project_relevance": round(project_relevance, 1),
            "assessment_readiness": round(assessment_readiness, 1),
        },
        "matched_skills": sorted(display_name.get(s, s) for s in (matched_must | matched_preferred)),
        "missing_must_have": sorted(display_name.get(s, s) for s in missing_must),
        "missing_preferred": sorted(display_name.get(s, s) for s in missing_preferred),
        "explanation": explanation,
    }
