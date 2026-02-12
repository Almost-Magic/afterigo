"""RepForecastHistory model — tracks stated vs actual probability per deal stage."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.deal import Deal


class RepForecastHistory(Base):
    __tablename__ = "rep_forecast_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    deal_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("deals.id"), nullable=False, index=True)
    stage: Mapped[str] = mapped_column(String(50), nullable=False)
    stated_probability: Mapped[int] = mapped_column(Integer, nullable=False)
    actual_outcome: Mapped[str | None] = mapped_column(String(20))
    deal_value: Mapped[float | None] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    deal: Mapped[Deal] = relationship("Deal", lazy="selectin")
