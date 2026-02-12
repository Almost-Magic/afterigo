"""Ripple CRM — Companies API routes."""

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.company import Company
from app.schemas.company import (
    CompanyCreate,
    CompanyListResponse,
    CompanyResponse,
    CompanyUpdate,
)
from app.services.audit import log_action, log_changes

router = APIRouter(prefix="/companies", tags=["companies"])


@router.post("", response_model=CompanyResponse, status_code=201)
async def create_company(data: CompanyCreate, db: AsyncSession = Depends(get_db)):
    company = Company(**data.model_dump())
    db.add(company)
    await db.flush()
    await log_action(db, "company", str(company.id), "create")
    await db.commit()
    await db.refresh(company)
    return company


@router.get("", response_model=CompanyListResponse)
async def list_companies(
    search: str | None = Query(None),
    industry: str | None = Query(None),
    sort_by: str = Query("created_at"),
    sort_dir: str = Query("desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(Company).where(Company.is_deleted == False)

    if search:
        term = f"%{search}%"
        q = q.where(
            or_(
                Company.name.ilike(term),
                Company.trading_name.ilike(term),
                Company.abn.ilike(term),
            )
        )
    if industry:
        q = q.where(Company.industry == industry)

    count_q = select(func.count()).select_from(q.subquery())
    total = (await db.execute(count_q)).scalar() or 0

    sort_col = getattr(Company, sort_by, Company.created_at)
    q = q.order_by(sort_col.desc() if sort_dir == "desc" else sort_col.asc())
    q = q.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(q)
    companies = result.scalars().all()

    return CompanyListResponse(items=companies, total=total, page=page, page_size=page_size)


@router.get("/{company_id}", response_model=CompanyResponse)
async def get_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.is_deleted == False)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: uuid.UUID, data: CompanyUpdate, db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.is_deleted == False)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    old_data = {k: getattr(company, k) for k in data.model_dump(exclude_unset=True)}
    update_data = data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(company, key, value)

    await log_changes(db, "company", str(company_id), old_data, update_data)
    await db.commit()
    await db.refresh(company)
    return company


@router.delete("/{company_id}")
async def delete_company(company_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Company).where(Company.id == company_id, Company.is_deleted == False)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    company.is_deleted = True
    await log_action(db, "company", str(company_id), "delete")
    await db.commit()
    return {"detail": "Company deleted"}
