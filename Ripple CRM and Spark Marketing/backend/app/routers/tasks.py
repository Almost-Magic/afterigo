"""Ripple CRM — Tasks API routes.

Tasks linked to contacts and/or deals. Filterable by status,
priority, and due date for daily action lists.
"""

import uuid
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.task import Task
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)
from app.services.audit import log_action, log_changes

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    """Create a new task, optionally linked to a contact and/or deal."""
    task = Task(**data.model_dump())
    db.add(task)
    await db.flush()
    await log_action(db, "task", str(task.id), "create")
    await db.commit()
    await db.refresh(task)
    return task


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: str | None = Query(None, description="Filter by status (todo/in_progress/done/cancelled)"),
    priority: str | None = Query(None, description="Filter by priority (low/medium/high/urgent)"),
    due_date: date | None = Query(None, description="Filter tasks due on this date"),
    overdue: bool | None = Query(None, description="Filter overdue tasks (due_date < today, not done)"),
    contact_id: uuid.UUID | None = Query(None, description="Filter by contact"),
    deal_id: uuid.UUID | None = Query(None, description="Filter by deal"),
    sort_by: str = Query("due_date"),
    sort_dir: str = Query("asc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """List tasks with optional filtering by status, priority, due date, and linked entities."""
    q = select(Task)

    if status:
        q = q.where(Task.status == status)
    if priority:
        q = q.where(Task.priority == priority)
    if due_date:
        q = q.where(Task.due_date == due_date)
    if overdue:
        today = date.today()
        q = q.where(Task.due_date < today, Task.status.notin_(["done", "cancelled"]))
    if contact_id:
        q = q.where(Task.contact_id == contact_id)
    if deal_id:
        q = q.where(Task.deal_id == deal_id)

    # Count total before pagination
    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    # Sort and paginate
    sort_col = getattr(Task, sort_by, Task.due_date)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    tasks = result.scalars().all()

    return TaskListResponse(items=tasks, total=total, page=page, page_size=page_size)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Fetch a single task by ID."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: uuid.UUID, data: TaskUpdate, db: AsyncSession = Depends(get_db)
):
    """Update a task — typically to change status or reassign priority."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    old_data = {k: getattr(task, k) for k in data.model_dump(exclude_unset=True)}
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(task, key, value)

    await log_changes(db, "task", str(task_id), old_data, update_data)
    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Delete a task (hard delete — tasks don't use soft-delete)."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    await log_action(db, "task", str(task_id), "delete")
    await db.delete(task)
    await db.commit()
    return {"detail": "Task deleted"}
