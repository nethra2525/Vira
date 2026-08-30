"""
Adaptive Assessment Engine.

Generates role-relevant question sets (mock mode: a curated bank keyed by
round type) and scores submissions against transparent rubrics. A live mode
could swap in generative question creation behind the same interface.
"""
from __future__ import annotations

APTITUDE_BANK = [
    {
        "prompt": "If a project takes 8 engineer-days and you have 4 engineers, how many days will it take working in parallel?",
        "options": ["1 day", "2 days", "4 days", "8 days"],
        "correct": "2 days",
    },
    {
        "prompt": "Choose the word that best completes: 'The recruiter's decision was ___ despite incomplete data.'",
        "options": ["Arbitrary", "Decisive", "Irrelevant", "Passive"],
        "correct": "Decisive",
    },
    {
        "prompt": "A dataset shows candidate scores rising 5% every assessment round. What trend is this?",
        "options": ["Linear growth", "Exponential decay", "Random noise", "No trend"],
        "correct": "Linear growth",
    },
]

TECHNICAL_BANK_BY_ROLE = {
    "software developer": [
        {"prompt": "Which data structure gives O(1) average lookup time?", "options": ["Array", "Linked List", "Hash Map", "Stack"], "correct": "Hash Map"},
        {"prompt": "What does SQL's GROUP BY clause do?", "options": ["Sorts rows", "Aggregates rows sharing values", "Filters rows", "Joins tables"], "correct": "Aggregates rows sharing values"},
    ],
    "data analyst": [
        {"prompt": "Which SQL clause filters aggregated results?", "options": ["WHERE", "HAVING", "ORDER BY", "LIMIT"], "correct": "HAVING"},
        {"prompt": "In Excel, which function looks up a value in a table?", "options": ["SUM", "VLOOKUP", "CONCAT", "ROUND"], "correct": "VLOOKUP"},
    ],
    "ui/ux designer": [
        {"prompt": "What is the primary goal of a usability test?", "options": ["Validate visual style", "Observe real user behavior against tasks", "Check code quality", "Measure server speed"], "correct": "Observe real user behavior against tasks"},
    ],
}

SCENARIO_BANK = [
    {
        "prompt": "Your project is close to the deadline, but a critical feature is failing. Describe your approach.",
    },
]


def generate_assessment_questions(round_type: str, job_title: str = "") -> list[dict]:
    if round_type == "aptitude":
        bank = APTITUDE_BANK
    elif round_type == "technical":
        bank = TECHNICAL_BANK_BY_ROLE.get(job_title.strip().lower(), TECHNICAL_BANK_BY_ROLE["software developer"])
    else:
        bank = SCENARIO_BANK

    questions = []
    for i, item in enumerate(bank):
        questions.append(
            {
                "question_type": "scenario" if round_type == "scenario" else "multiple_choice",
                "prompt": item["prompt"],
                "options": item.get("options", []),
                "correct_option": item.get("correct", ""),
            }
        )
    return questions


def score_multiple_choice(answers: list[dict], questions: list[dict]) -> dict:
    """answers/questions are lists of dicts with matching order; scores exact-match MCQs."""
    if not questions:
        return {"score": 0.0, "breakdown": {}, "feedback": "No questions to score."}

    correct = 0
    for q, a in zip(questions, answers):
        if q.get("correct_option") and a.get("answer_text", "").strip().lower() == q["correct_option"].strip().lower():
            correct += 1

    score = round((correct / len(questions)) * 100, 1)
    feedback = (
        f"You answered {correct} of {len(questions)} correctly. "
        + ("Strong performance." if score >= 75 else "Consider reviewing the areas you missed before your next attempt.")
    )
    return {
        "score": score,
        "breakdown": {"correct": correct, "total": len(questions)},
        "feedback": feedback,
    }


def score_scenario_response(answer_text: str) -> dict:
    """Transparent rubric scoring: clarity, relevance, problem-solving approach, completeness.
    Mock mode uses simple heuristics (length/keyword presence) -- never claims to detect
    personality or emotion, per the Responsible AI requirements."""
    text = answer_text or ""
    word_count = len(text.split())

    clarity = min(100, 40 + word_count * 2) if word_count > 5 else 20
    relevance = 80 if any(kw in text.lower() for kw in ["deadline", "priorit", "communicat", "test", "risk"]) else 50
    problem_solving = 80 if any(kw in text.lower() for kw in ["would", "plan", "approach", "steps", "first"]) else 50
    completeness = min(100, word_count * 3) if word_count < 34 else 100

    overall = round((clarity + relevance + problem_solving + completeness) / 4, 1)

    return {
        "score": overall,
        "breakdown": {
            "clarity": clarity,
            "relevance": relevance,
            "problem_solving_approach": problem_solving,
            "completeness": completeness,
        },
        "feedback": "Scored against a transparent rubric: clarity, relevance, problem-solving approach, and completeness. "
        "This reflects structured criteria only -- not emotion or personality assessment.",
    }
