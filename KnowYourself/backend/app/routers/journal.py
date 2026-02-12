"""KnowYourself — Journal (Daily Inquiry) API routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.journal import JournalEntry
from app.schemas.assessment import JournalResult, JournalSubmission
from app.services.ollama import reflect_on_journal

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["journal"])


@router.post("/journal", response_model=JournalResult)
async def submit_journal(submission: JournalSubmission, db: AsyncSession = Depends(get_db)):
    if not submission.entry_text.strip():
        raise HTTPException(400, "Journal entry cannot be empty")
    if len(submission.entry_text) > 10000:
        raise HTTPException(400, "Journal entry must be under 10,000 characters")

    reflection, themes = await reflect_on_journal(submission.prompt, submission.entry_text)

    record = JournalEntry(
        prompt=submission.prompt,
        entry_text=submission.entry_text,
        ai_reflection=reflection,
        themes=themes,
    )
    db.add(record)
    await db.commit()
    await db.refresh(record)

    return JournalResult(
        id=str(record.id),
        prompt=record.prompt,
        entry_text=record.entry_text,
        ai_reflection=record.ai_reflection,
        themes=record.themes,
        created_at=record.created_at,
    )
