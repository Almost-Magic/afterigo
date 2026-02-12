"""KnowYourself — Assessment schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# --- Big Five ---

class BigFiveSubmission(BaseModel):
    answers: list[int]  # 50 integers, each 1-5


class BigFiveScores(BaseModel):
    openness: float
    conscientiousness: float
    extraversion: float
    agreeableness: float
    neuroticism: float


class BigFiveResult(BaseModel):
    id: str
    scores: BigFiveScores
    ai_interpretation: Optional[str] = None
    created_at: datetime


# --- Archetype ---

class ArchetypeSubmission(BaseModel):
    answers: list[str]  # 24 strings, each "A" or "B"


class ArchetypeResult(BaseModel):
    id: str
    primary_archetype: str
    shadow_archetype: str
    percentages: dict[str, float]
    ai_interpretation: Optional[str] = None
    created_at: datetime


# --- Consciousness ---

class ConsciousnessSubmission(BaseModel):
    answers: list[int]  # 10 integers, each 1-5


class ConsciousnessResult(BaseModel):
    id: str
    level: int
    level_name: str
    ai_interpretation: Optional[str] = None
    created_at: datetime


# --- Journal ---

class JournalSubmission(BaseModel):
    prompt: str = "Who am I today?"
    entry_text: str


class JournalResult(BaseModel):
    id: str
    prompt: str
    entry_text: str
    ai_reflection: Optional[str] = None
    themes: Optional[list[str]] = None
    created_at: datetime


# --- History / Profile ---

class AssessmentSummary(BaseModel):
    id: str
    assessment_type: str
    scores: dict
    created_at: datetime


class ProfileResponse(BaseModel):
    latest_big_five: Optional[BigFiveScores] = None
    latest_archetype: Optional[dict] = None
    latest_consciousness: Optional[dict] = None
    total_assessments: int
    total_journal_entries: int
    journal_themes: list[str]
