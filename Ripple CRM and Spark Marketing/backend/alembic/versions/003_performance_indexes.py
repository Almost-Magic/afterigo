"""Add performance indexes.

Revision ID: 003_perf
Revises: 58ebd3922c0e
"""
from alembic import op

revision = "003_perf"
down_revision = "58ebd3922c0e"


def upgrade():
    # Contacts — email and company_id already indexed in initial migration
    op.create_index("ix_contacts_type", "contacts", ["type"])
    op.create_index("ix_contacts_created_at", "contacts", ["created_at"])
    # Deals — stage, contact_id, company_id, created_at already indexed
    # (no new deal indexes needed)
    # Interactions — contact_id already indexed
    op.create_index("ix_interactions_type", "interactions", ["type"])
    op.create_index("ix_interactions_occurred_at", "interactions", ["occurred_at"])
    # Tasks — contact_id and deal_id already indexed
    op.create_index("ix_tasks_status", "tasks", ["status"])
    op.create_index("ix_tasks_due_date", "tasks", ["due_date"])
    # Commitments — contact_id and deal_id already indexed
    op.create_index("ix_commitments_status", "commitments", ["status"])
    op.create_index("ix_commitments_due_date", "commitments", ["due_date"])
    # Notes — contact_id already indexed
    op.create_index("ix_notes_deal_id", "notes", ["deal_id"])
    # Audit log — entity_type already indexed; uses changed_at not created_at
    op.create_index("ix_audit_log_changed_at", "audit_log", ["changed_at"])


def downgrade():
    for name in [
        "ix_contacts_type", "ix_contacts_created_at",
        "ix_interactions_type", "ix_interactions_occurred_at",
        "ix_tasks_status", "ix_tasks_due_date",
        "ix_commitments_status", "ix_commitments_due_date",
        "ix_notes_deal_id",
        "ix_audit_log_changed_at",
    ]:
        op.drop_index(name)
