"""KnowYourself — History and Profile API routes."""

from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.assessment import Assessment
from app.models.journal import JournalEntry
from app.schemas.assessment import AssessmentSummary, BigFiveScores, ProfileResponse

router = APIRouter(prefix="/api", tags=["history"])


@router.get("/history", response_model=list[AssessmentSummary])
async def get_history(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Assessment).order_by(Assessment.created_at.desc()).limit(100)
    )
    assessments = result.scalars().all()
    return [
        AssessmentSummary(
            id=str(a.id),
            assessment_type=a.assessment_type,
            scores=a.scores,
            created_at=a.created_at,
        )
        for a in assessments
    ]


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(db: AsyncSession = Depends(get_db)):
    # Latest Big Five
    bf_result = await db.execute(
        select(Assessment)
        .where(Assessment.assessment_type == "big_five")
        .order_by(Assessment.created_at.desc())
        .limit(1)
    )
    bf = bf_result.scalar_one_or_none()

    # Latest Archetype
    arch_result = await db.execute(
        select(Assessment)
        .where(Assessment.assessment_type == "archetype")
        .order_by(Assessment.created_at.desc())
        .limit(1)
    )
    arch = arch_result.scalar_one_or_none()

    # Latest Consciousness
    con_result = await db.execute(
        select(Assessment)
        .where(Assessment.assessment_type == "consciousness")
        .order_by(Assessment.created_at.desc())
        .limit(1)
    )
    con = con_result.scalar_one_or_none()

    # Counts
    total_result = await db.execute(select(Assessment))
    total_assessments = len(total_result.scalars().all())

    journal_result = await db.execute(select(JournalEntry))
    entries = journal_result.scalars().all()
    total_journal = len(entries)

    # Aggregate journal themes
    all_themes = []
    for entry in entries:
        if entry.themes:
            all_themes.extend(entry.themes)
    theme_counts = Counter(all_themes)
    top_themes = [t for t, _ in theme_counts.most_common(20)]

    return ProfileResponse(
        latest_big_five=BigFiveScores(**bf.scores) if bf else None,
        latest_archetype=arch.scores if arch else None,
        latest_consciousness=con.scores if con else None,
        total_assessments=total_assessments,
        total_journal_entries=total_journal,
        journal_themes=top_themes,
    )
