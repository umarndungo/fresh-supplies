"""add commodity_class to produce

Revision ID: 0001_add_commodity_class
Revises: 0000_initial
Create Date: 2026-08-31

Note: commodity_class is now part of the 0000_initial base schema, so this
migration exists solely to preserve history for databases that predate the
squashed initial migration. Upgrade/Downgrade are no-ops.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_add_commodity_class"
down_revision = "0000_initial"
branch_labels = None
depends_on = None

commodity_class_enum = postgresql.ENUM(
    "PERISHABLE", "STAPLE", name="commodity_class", create_type=False
)


def upgrade() -> None:
    # Column already provided by 0000_initial; nothing to do for databases
    # that already have the full schema.
    pass


def downgrade() -> None:
    pass
