"""
Interview Assistant module (powers VIRA CALL).

Manages a scripted-but-adaptive question flow with follow-ups. Speech-to-text
and text-to-speech are abstracted behind `TranscribeProvider` / `SpeakProvider`
so a real speech vendor can be dropped in later; mock mode simply echoes
provided text, which lets the full interview UI/state machine be built and
tested without any external API key.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

BASE_QUESTIONS = [
    "Tell me about a project you're proud of and the problem it solved.",
    "Walk me through how you approached a recent technical challenge.",
    "How do you prioritize when multiple deadlines overlap?",
    "What's an area you're actively trying to improve, and how?",
]

FOLLOW_UP_TRIGGERS = {
    "challenge": "What would you do differently if you faced that challenge again?",
    "team": "How did you handle disagreement within the team?",
    "deadline": "How did you communicate progress to stakeholders during that time?",
}


class TranscribeProvider(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes) -> str: ...


class MockTranscribeProvider(TranscribeProvider):
    def transcribe(self, audio_bytes: bytes) -> str:
        # In mock mode the frontend sends text directly instead of audio.
        return ""


def next_question(question_index: int, previous_answer: str | None = None) -> dict | None:
    if previous_answer:
        lowered = previous_answer.lower()
        for trigger, follow_up in FOLLOW_UP_TRIGGERS.items():
            if trigger in lowered:
                return {"prompt": follow_up, "is_follow_up": True}

    if question_index >= len(BASE_QUESTIONS):
        return None
    return {"prompt": BASE_QUESTIONS[question_index], "is_follow_up": False}


def build_interview_summary(responses: list[dict]) -> str:
    if not responses:
        return "No responses were recorded for this session."
    answered = len(responses)
    avg_len = sum(len(r.get("transcript", "").split()) for r in responses) / max(answered, 1)
    depth = "detailed" if avg_len > 25 else "concise"
    return (
        f"Completed {answered} question(s) with {depth} responses overall. "
        "This summary reflects structured transcript analysis only -- VIRA does not detect "
        "emotion, personality, or truthfulness. A human reviewer should evaluate the full transcript."
    )
