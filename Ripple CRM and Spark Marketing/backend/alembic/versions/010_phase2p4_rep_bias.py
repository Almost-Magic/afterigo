"""Phase 2.4: Rep Bias Brain.

New table: rep_forecast_history.
New columns on contacts: rep_bias_factor, rep_bias_direction.

Revision ID: 010_rep_bias
Revises: 009_pulse
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision = "010_rep_bias"
down_revision = "009_pulse"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "rep_forecast_history",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("deal_id", UUID(as_uuid=True), sa.ForeignKey("deals.id"), nullable=False, index=True),
        sa.Column("stage", sa.String(50), nullable=False),
        sa.Column("stated_probability", sa.Integer, nullable=False),
        sa.Column("actual_outcome", sa.String(20), nullable=True),
        sa.Column("deal_value", sa.Float, nullable=True),
        sa.Column("recorded_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("rep_forecast_history")
