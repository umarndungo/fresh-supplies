"""create cooperative_access_grants

Revision ID: 20260918_access_grants
Revises: 20260918_cooperative_role

See backend/docs/multitenancy_design.md §2.4. One row = "this
LOGISTICS_MANAGER/MARKET_ANALYST can see this cooperative's shipments and
produce." Application-level rule (enforced in the repository, not the DB):
user_id must belong to a LOGISTICS_MANAGER or MARKET_ANALYST account —
ADMINISTRATOR is never a valid grantee (§7.3 of the design doc).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260918_access_grants"
down_revision = "20260918_cooperative_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "cooperative_access_grants",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "cooperative_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cooperatives.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("granted_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "cooperative_id", name="uq_cooperative_access_grants_user_coop"),
    )
    op.create_index("ix_cooperative_access_grants_user_id", "cooperative_access_grants", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_cooperative_access_grants_user_id", table_name="cooperative_access_grants")
    op.drop_table("cooperative_access_grants")
