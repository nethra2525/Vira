"""
VIRA Growth Path generator.

Turns a match result into supportive, actionable guidance instead of a bare
rejection -- the "second-chance hiring" system described in the product spec.
"""
from __future__ import annotations


def build_growth_path(
    matched_skills: list[str],
    missing_must_have: list[str],
    missing_preferred: list[str],
    current_match: float,
    previous_match: float | None = None,
) -> dict:
    skills_to_improve = missing_must_have + missing_preferred

    steps = []
    order = 1
    for skill in missing_must_have:
        steps.append({"order": order, "action": f"Build a short project or complete a course covering {skill}.", "related_skill": skill})
        order += 1
    for skill in missing_preferred[:2]:
        steps.append({"order": order, "action": f"Strengthen {skill} through a focused practice exercise.", "related_skill": skill})
        order += 1
    steps.append({"order": order, "action": "Complete the suggested skill assessment to demonstrate improvement.", "related_skill": None})
    order += 1
    steps.append({"order": order, "action": "Request reassessment once you've completed the steps above.", "related_skill": None})

    return {
        "current_match": current_match,
        "previous_match": previous_match,
        "strengths": matched_skills,
        "skills_to_improve": skills_to_improve,
        "steps": steps,
        "progress": 0.0 if previous_match is None else max(0.0, round(current_match - previous_match, 1)),
    }
