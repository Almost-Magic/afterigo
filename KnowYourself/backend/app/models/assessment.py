"""KnowYourself — Assessment model."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, String, Text
from sqlalchemy.dialects.postgresql import JSON, UUID

from app.models.base import Base


class Assessment(Base):
    __tablename__ = "assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    assessment_type = Column(String(50), nullable=False, index=True)  # big_five | archetype | consciousness
    answers = Column(JSON, nullable=False)
    scores = Column(JSON, nullable=False)
    ai_interpretation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
