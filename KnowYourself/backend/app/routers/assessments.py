"""KnowYourself — Assessment API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.assessment import Assessment
from app.schemas.assessment import (
    ArchetypeResult,
    ArchetypeSubmission,
    BigFiveResult,
    BigFiveScores,
    BigFiveSubmission,
    ConsciousnessResult,
    ConsciousnessSubmission,
)
from app.services.ollama import interpret_archetype, interpret_big_five, interpret_consciousness
from app.services.scoring import score_archetype, score_big_five, score_consciousness

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assessments", tags=["assessments"])


@router.post("/big-five", response_model=BigFiveResult)
async def submit_big_five(submission: BigFiveSubmission, db: AsyncSession = Depends(get_db)):
    if len(submission.answers) != 50:
        raise HTTPException(400, f"Expected 50 answers, got {len(submission.answers)}")
    for i, a in enumerate(submission.answers):
        if a < 1 or a > 5:
            raise HTTPException(400, f"Answer {i+1} must be 1-5, got {a}")

    scores = score_big_five(submission.answers)
    interpretation = await interpret_big_five(scores)

    record = Assessment(
        assessment_type="big_five",
        answers=submission.answers,
        scores=scores,
        ai_interpretation=interpretation,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return BigFiveResult(
        id=str(record.id),
        scores=BigFiveScores(**scores),
        ai_interpretation=interpretation,
        created_at=record.created_at,
    )


@router.post("/archetype", response_model=ArchetypeResult)
async def submit_archetype(submission: ArchetypeSubmission, db: AsyncSession = Depends(get_db)):
    if len(submission.answers) != 24:
        raise HTTPException(400, f"Expected 24 answers, got {len(submission.answers)}")
    for i, a in enumerate(submission.answers):
        if a.upper() not in ("A", "B"):
            raise HTTPException(400, f"Answer {i+1} must be 'A' or 'B', got '{a}'")

    result = score_archetype(submission.answers)
    interpretation = await interpret_archetype(
        result["primary_archetype"],
        result["shadow_archetype"],
        result["percentages"],
    )

    record = Assessment(
        assessment_type="archetype",
        answers=submission.answers,
        scores=result,
        ai_interpretation=interpretation,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return ArchetypeResult(
        id=str(record.id),
        primary_archetype=result["primary_archetype"],
        shadow_archetype=result["shadow_archetype"],
        percentages=result["percentages"],
        ai_interpretation=interpretation,
        created_at=record.created_at,
    )


@router.post("/consciousness", response_model=ConsciousnessResult)
async def submit_consciousness(submission: ConsciousnessSubmission, db: AsyncSession = Depends(get_db)):
    if len(submission.answers) != 10:
        raise HTTPException(400, f"Expected 10 answers, got {len(submission.answers)}")
    for i, a in enumerate(submission.answers):
        if a < 1 or a > 5:
            raise HTTPException(400, f"Answer {i+1} must be 1-5, got {a}")

    result = score_consciousness(submission.answers)
    interpretation = await interpret_consciousness(result["level"], result["level_name"])

    record = Assessment(
        assessment_type="consciousness",
        answers=submission.answers,
        scores=result,
        ai_interpretation=interpretation,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return ConsciousnessResult(
        id=str(record.id),
        level=result["level"],
        level_name=result["level_name"],
        ai_interpretation=interpretation,
        created_at=record.created_at,
    )
