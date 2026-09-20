"""add DRIVER role and driver_user_id assignment on shipments

Revision ID: 20260918_driver_role
Revises: 20260918_access_grants

Phase 2 (driver assignment) per the implementation plan: a shipment gets a
real driver_user_id FK instead of a free-text name, and DRIVER becomes a
real role so a driver account's manifest can be scoped to exactly the
shipments assigned to them (see backend/docs/multitenancy_design.md's
tenancy.VisibilityScope, extended with assigned_driver_id).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260918_driver_role"
down_revision = "20260918_access_grants"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres allows adding an enum value inside a transaction; the new
    # value just can't be *used* until this transaction commits. Nothing in
    # this migration references 'DRIVER', so that's not an issue here.
    op.execute("ALTER TYPE user_role ADD VALUE IF NOT EXISTS 'DRIVER'")

    op.add_column("shipments", sa.Column("driver_user_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_shipments_driver_user_id", "shipments", "users", ["driver_user_id"], ["id"])
    op.create_index("ix_shipments_driver_user_id", "shipments", ["driver_user_id"])


def downgrade() -> None:
    op.drop_index("ix_shipments_driver_user_id", table_name="shipments")
    op.drop_constraint("fk_shipments_driver_user_id", "shipments", type_="foreignkey")
    op.drop_column("shipments", "driver_user_id")
    # Postgres has no ALTER TYPE ... DROP VALUE; removing 'DRIVER' from the
    # user_role enum would require recreating the type and every column that
    # uses it. Left as a no-op — the enum value is purely additive with no
    # other schema to unwind.
