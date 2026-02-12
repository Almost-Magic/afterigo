"""Ripple CRM — Attention Allocation schemas."""

from pydantic import BaseModel


class AllocationEntry(BaseModel):
    contact_id: str
    contact_name: str
    company_name: str | None = None
    time_spent_minutes: int = 0
    time_spent_pct: float = 0.0
    revenue_potential: float = 0.0
    revenue_potential_pct: float = 0.0
    allocation_ratio: float | None = None
    status: str = "no_deals"
    deal_count: int = 0


class AllocationSummary(BaseModel):
    period_days: int = 30
    total_time_minutes: int = 0
    total_revenue_potential: float = 0.0
    well_allocated: int = 0
    overallocated: int = 0
    underallocated: int = 0
    no_deals: int = 0
    allocations: list[AllocationEntry] = []


class ContactAllocationDetail(BaseModel):
    contact_id: str
    contact_name: str
    company_name: str | None = None
    period_days: int = 30
    time_spent_minutes: int = 0
    time_by_type: dict[str, int] = {}
    time_pct: float = 0.0
    deals: list[dict] = []
    revenue_potential: float = 0.0
    revenue_pct: float = 0.0
    allocation_ratio: float | None = None
    status: str = "no_deals"


class Recommendation(BaseModel):
    type: str  # "increase_attention" | "reduce_attention"
    priority: str  # "high" | "medium" | "low"
    contact_id: str
    contact_name: str
    revenue_potential: float = 0.0
    current_time_pct: float = 0.0
    suggested_time_pct: float | None = None
    reason: str = ""


class RecommendationList(BaseModel):
    period_days: int = 30
    items: list[Recommendation] = []
    total: int = 0
