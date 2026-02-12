"""KnowYourself — Question bank API routes."""

import random
from datetime import date

from fastapi import APIRouter

from app.services.questions import (
    ARCHETYPE_QUESTIONS,
    BIG_FIVE_QUESTIONS,
    CONSCIOUSNESS_QUESTIONS,
    DAILY_PROMPTS,
)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/big-five")
async def get_big_five_questions():
    return {"questions": BIG_FIVE_QUESTIONS, "total": len(BIG_FIVE_QUESTIONS)}


@router.get("/archetype")
async def get_archetype_questions():
    return {"questions": ARCHETYPE_QUESTIONS, "total": len(ARCHETYPE_QUESTIONS)}


@router.get("/consciousness")
async def get_consciousness_questions():
    return {"questions": CONSCIOUSNESS_QUESTIONS, "total": len(CONSCIOUSNESS_QUESTIONS)}


@router.get("/daily-prompt")
async def get_daily_prompt():
    today = date.today()
    idx = today.toordinal() % len(DAILY_PROMPTS)
    return {"prompt": DAILY_PROMPTS[idx], "all_prompts": DAILY_PROMPTS}
