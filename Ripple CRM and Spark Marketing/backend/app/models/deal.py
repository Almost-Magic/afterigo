"""Ripple CRM — Deal model."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.commitment import Commitment
    from app.models.company import Company
    from app.models.contact import Contact
    from app.models.note import Note
    from app.models.task import Task


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    contact_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("contacts.id"), nullable=True, index=True)
    company_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    value: Mapped[float | None] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="AUD")
    stage: Mapped[str] = mapped_column(String(30), default="lead", index=True)
    probability: Mapped[float | None] = mapped_column(Float)
    expected_close_date: Mapped[date | None] = mapped_column(Date)
    actual_close_date: Mapped[date | None] = mapped_column(Date)
    owner: Mapped[str | None] = mapped_column(String(100))
    source: Mapped[str | None] = mapped_column(String(100))
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    contact: Mapped[Contact | None] = relationship("Contact", back_populates="deals", foreign_keys=[contact_id])
    company: Mapped[Company | None] = relationship("Company", back_populates="deals")
    commitments: Mapped[list[Commitment]] = relationship("Commitment", back_populates="deal", lazy="selectin")
    tasks: Mapped[list[Task]] = relationship("Task", back_populates="deal", lazy="selectin")
    notes_list: Mapped[list[Note]] = relationship("Note", back_populates="deal", lazy="selectin")
