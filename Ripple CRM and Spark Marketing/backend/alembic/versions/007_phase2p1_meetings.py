"""Phase 2.1: Meeting Intelligence Hub.

New tables: meetings, meeting_actions.

Revision ID: 007_meetings
Revises: 006_phase3
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "007_meetings"
down_revision = "006_phase3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "meetings",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=False, index=True),
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("deals.id"), nullable=True, index=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("meeting_type", sa.String(20), nullable=False, server_default="in_person"),
        sa.Column("location", sa.String(500), nullable=True),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("duration_minutes", sa.Integer, nullable=True),
        sa.Column("outcome", sa.String(20), nullable=True),
        sa.Column("attendees_json", sa.Text, nullable=True),
        sa.Column("agenda", sa.Text, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("topics_json", sa.Text, nullable=True),
        sa.Column("next_steps", sa.Text, nullable=True),
        sa.Column("sentiment_score", sa.Float, nullable=True),
        sa.Column("ai_summary", sa.Text, nullable=True),
        sa.Column("prep_brief_json", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "meeting_actions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("meeting_id", UUID(as_uuid=True), sa.ForeignKey("meetings.id", ondelete="CASCADE"), nullable=False, index=True),
        sa.Column("contact_id", UUID(as_uuid=True), sa.ForeignKey("contacts.id"), nullable=True, index=True),
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("deals.id"), nullable=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("assignee", sa.String(100), nullable=True),
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("priority", sa.String(10), server_default="medium"),
        sa.Column("status", sa.String(20), server_default="todo"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("meeting_actions")
    op.drop_table("meetings")
