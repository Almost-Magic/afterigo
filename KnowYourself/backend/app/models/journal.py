"""KnowYourself — Journal entry model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID

from app.models.base import Base


class JournalEntry(Base):
    __tablename__ = "journal_entries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = Column(String(200), nullable=False)
    entry_text = Column(Text, nullable=False)
    ai_reflection = Column(Text, nullable=True)
    themes = Column(JSON, nullable=True)  # list of extracted theme strings
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
