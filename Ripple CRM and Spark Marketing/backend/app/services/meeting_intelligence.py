"""Meeting Intelligence service — Prep Me briefs and analytics."""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone

import httpx
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.commitment import Commitment
from app.models.contact import Contact
from app.models.deal import Deal
from app.models.interaction import Interaction
from app.models.meeting import Meeting, MeetingAction
from app.models.task import Task

log = logging.getLogger(__name__)

SUPERVISOR_URL = "http://localhost:9000"


async def generate_prep_brief(db: AsyncSession, meeting_id) -> dict:
    """Generate a 'Prep Me' brief for an upcoming meeting.

    Gathers contact history, deal status, recent interactions, open
    commitments/tasks, and optionally enriches with AI via Supervisor.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        return {}

    contact = await db.get(Contact, meeting.contact_id)
    if not contact:
        return {}

    # ── Gather context ───────────────────────────────────────────────
    deal = await db.get(Deal, meeting.deal_id) if meeting.deal_id else None

    # Recent interactions (last 10)
    q = (
        select(Interaction)
        .where(Interaction.contact_id == contact.id)
        .order_by(Interaction.occurred_at.desc())
        .limit(10)
    )
    result = await db.execute(q)
    interactions = result.scalars().all()
    recent_interactions = [
        {
            "type": i.type,
            "subject": i.subject,
            "occurred_at": i.occurred_at.isoformat() if i.occurred_at else None,
            "sentiment": i.sentiment_score,
            "channel": i.channel,
        }
        for i in interactions
    ]

    # Open commitments
    q = (
        select(Commitment)
        .where(Commitment.contact_id == contact.id, Commitment.status == "pending")
        .order_by(Commitment.due_date.asc().nullslast())
        .limit(10)
    )
    result = await db.execute(q)
    commitments = result.scalars().all()
    open_commitments = [
        {
            "description": c.description,
            "committed_by": c.committed_by,
            "due_date": c.due_date.isoformat() if c.due_date else None,
        }
        for c in commitments
    ]

    # Open tasks
    q = (
        select(Task)
        .where(Task.contact_id == contact.id, Task.status.in_(["todo", "in_progress"]))
        .order_by(Task.due_date.asc().nullslast())
        .limit(10)
    )
    result = await db.execute(q)
    tasks = result.scalars().all()
    open_tasks = [
        {
            "title": t.title,
            "priority": t.priority,
            "due_date": t.due_date.isoformat() if t.due_date else None,
        }
        for t in tasks
    ]

    # Relationship health (from service)
    from app.services.relationship_health import calculate_health_score
    health = await calculate_health_score(db, contact.id)

    # ── Build brief ──────────────────────────────────────────────────
    contact_name = f"{contact.first_name} {contact.last_name}"
    brief = {
        "meeting_id": str(meeting.id),
        "contact_name": contact_name,
        "deal_title": deal.title if deal else None,
        "deal_stage": deal.stage if deal else None,
        "deal_value": float(deal.value) if deal and deal.value else None,
        "relationship_health": health,
        "recent_interactions": recent_interactions,
        "open_commitments": open_commitments,
        "open_tasks": open_tasks,
        "suggested_talking_points": [],
        "ai_summary": None,
    }

    # ── Heuristic talking points ─────────────────────────────────────
    talking_points = []
    if health and health.get("score", 0) < 50:
        talking_points.append("Relationship health is low — focus on rebuilding trust.")
    if open_commitments:
        overdue = [c for c in commitments if c.due_date and c.due_date < datetime.now(timezone.utc).date()]
        if overdue:
            talking_points.append(f"{len(overdue)} overdue commitment(s) — address these first.")
        talking_points.append(f"{len(open_commitments)} open commitment(s) to review.")
    if deal:
        talking_points.append(f"Deal '{deal.title}' is in '{deal.stage}' stage.")
        if deal.value:
            talking_points.append(f"Deal value: ${deal.value:,.2f}")
    if not interactions:
        talking_points.append("No prior interactions on record — this is a first meeting.")
    elif len(interactions) >= 1:
        last = interactions[0]
        talking_points.append(f"Last interaction: {last.type} on {last.occurred_at.strftime('%d %b %Y') if last.occurred_at else 'unknown'}.")

    brief["suggested_talking_points"] = talking_points

    # ── AI enrichment via Supervisor (optional) ──────────────────────
    try:
        ai_prompt = (
            f"You are a CRM assistant preparing a meeting brief. "
            f"Contact: {contact_name}. "
            f"{'Deal: ' + deal.title + ' (' + deal.stage + ').' if deal else 'No active deal.'} "
            f"Recent interactions: {len(interactions)}. "
            f"Open commitments: {len(open_commitments)}. "
            f"Relationship health: {health.get('label', 'Unknown') if health else 'Unknown'}. "
            f"Generate 3 concise talking points for the meeting, Australian business style."
        )
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{SUPERVISOR_URL}/api/chat",
                json={
                    "model": "gemma2:27b",
                    "messages": [{"role": "user", "content": ai_prompt}],
                    "stream": False,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                ai_text = data.get("message", {}).get("content", "")
                if ai_text:
                    brief["ai_summary"] = ai_text
    except Exception as e:
        log.info(f"AI enrichment skipped (Supervisor unavailable): {e}")

    # Save brief to meeting record
    meeting.prep_brief_json = json.dumps(brief)
    await db.commit()

    return brief


async def process_followup(
    db: AsyncSession,
    meeting_id,
    notes: str | None = None,
    outcome: str | None = None,
    topics_json: str | None = None,
    next_steps: str | None = None,
    sentiment_score: float | None = None,
    actions: list[dict] | None = None,
    auto_create_tasks: bool = True,
    auto_create_commitments: bool = True,
) -> dict:
    """Process 'Follow Me' post-meeting data.

    Updates meeting record, creates MeetingActions, and optionally
    auto-creates Tasks and Commitments from the actions.
    """
    meeting = await db.get(Meeting, meeting_id)
    if not meeting:
        return {"error": "Meeting not found"}

    # Update meeting fields
    if notes is not None:
        meeting.notes = notes
    if outcome is not None:
        meeting.outcome = outcome
    if topics_json is not None:
        meeting.topics_json = topics_json
    if next_steps is not None:
        meeting.next_steps = next_steps
    if sentiment_score is not None:
        meeting.sentiment_score = sentiment_score
    meeting.updated_at = datetime.now(timezone.utc)

    actions_created = 0
    tasks_created = 0
    commitments_created = 0

    # Create meeting actions
    for action_data in (actions or []):
        action = MeetingAction(
            meeting_id=meeting.id,
            contact_id=meeting.contact_id,
            deal_id=meeting.deal_id,
            title=action_data.get("title", "Follow-up"),
            description=action_data.get("description"),
            assignee=action_data.get("assignee"),
            due_date=action_data.get("due_date"),
            priority=action_data.get("priority", "medium"),
        )
        db.add(action)
        actions_created += 1

        # Auto-create task
        if auto_create_tasks:
            task = Task(
                contact_id=meeting.contact_id,
                deal_id=meeting.deal_id,
                title=f"[Meeting] {action_data.get('title', 'Follow-up')}",
                description=f"From meeting: {meeting.title}\n{action_data.get('description', '')}",
                due_date=action_data.get("due_date"),
                priority=action_data.get("priority", "medium"),
            )
            db.add(task)
            tasks_created += 1

        # Auto-create commitment
        if auto_create_commitments:
            commitment = Commitment(
                contact_id=meeting.contact_id,
                deal_id=meeting.deal_id,
                description=action_data.get("title", "Follow-up"),
                committed_by="us",
                due_date=action_data.get("due_date"),
            )
            db.add(commitment)
            commitments_created += 1

    await db.commit()
    await db.refresh(meeting)

    return {
        "meeting": meeting,
        "actions_created": actions_created,
        "tasks_created": tasks_created,
        "commitments_created": commitments_created,
    }


async def calculate_meeting_analytics(db: AsyncSession) -> dict:
    """Aggregate meeting analytics across all meetings."""
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # Total meetings
    total_q = select(func.count(Meeting.id))
    total = (await db.execute(total_q)).scalar() or 0

    # Meetings this month
    month_q = select(func.count(Meeting.id)).where(Meeting.scheduled_at >= month_start)
    meetings_month = (await db.execute(month_q)).scalar() or 0

    # Average duration
    dur_q = select(func.avg(Meeting.duration_minutes)).where(Meeting.duration_minutes.isnot(None))
    avg_dur = (await db.execute(dur_q)).scalar()

    # Outcomes breakdown
    outcome_q = select(Meeting.outcome, func.count(Meeting.id)).where(Meeting.outcome.isnot(None)).group_by(Meeting.outcome)
    outcome_rows = (await db.execute(outcome_q)).all()
    outcomes = {row[0]: row[1] for row in outcome_rows}

    # Type breakdown
    type_q = select(Meeting.meeting_type, func.count(Meeting.id)).group_by(Meeting.meeting_type)
    type_rows = (await db.execute(type_q)).all()
    by_type = {row[0]: row[1] for row in type_rows}

    # Action stats
    actions_total_q = select(func.count(MeetingAction.id))
    actions_total = (await db.execute(actions_total_q)).scalar() or 0

    actions_done_q = select(func.count(MeetingAction.id)).where(MeetingAction.status == "done")
    actions_done = (await db.execute(actions_done_q)).scalar() or 0

    completion_rate = (actions_done / actions_total * 100) if actions_total > 0 else None

    # Top contacts by meeting count
    top_q = (
        select(Meeting.contact_id, func.count(Meeting.id).label("cnt"))
        .group_by(Meeting.contact_id)
        .order_by(func.count(Meeting.id).desc())
        .limit(5)
    )
    top_rows = (await db.execute(top_q)).all()
    top_contacts = []
    for row in top_rows:
        contact = await db.get(Contact, row[0])
        if contact:
            top_contacts.append({
                "contact_id": str(row[0]),
                "contact_name": f"{contact.first_name} {contact.last_name}",
                "meeting_count": row[1],
            })

    return {
        "total_meetings": total,
        "meetings_this_month": meetings_month,
        "avg_duration_minutes": round(avg_dur, 1) if avg_dur else None,
        "outcomes": outcomes,
        "meetings_by_type": by_type,
        "actions_total": actions_total,
        "actions_completed": actions_done,
        "actions_completion_rate": round(completion_rate, 1) if completion_rate else None,
        "top_contacts": top_contacts,
    }
