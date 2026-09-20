"""add cooperative_role to users

Revision ID: 20260918_cooperative_role
Revises: 20260918_produce_tenant_fields

See backend/docs/multitenancy_design.md §2.3. NULL for anyone without a
cooperative_id (solo farmers, platform staff, administrators) — meaningless
outside a cooperative context.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260918_cooperative_role"
down_revision = "20260918_produce_tenant_fields"
branch_labels = None
depends_on = None

cooperative_role_enum = postgresql.ENUM(
    "MEMBER", "ADMIN", name="cooperative_role_enum", create_type=False,
)


def upgrade() -> None:
    cooperative_role_enum.create(op.get_bind(), checkfirst=True)
    op.add_column("users", sa.Column("cooperative_role", cooperative_role_enum, nullable=True))

    # Whoever created a cooperative is its first admin.
    op.execute(
        """
        UPDATE users u
        SET cooperative_role = 'ADMIN'
        FROM cooperatives c
        WHERE c.created_by = u.id
        """
    )
    # Everyone else already in a cooperative defaults to MEMBER.
    op.execute(
        "UPDATE users SET cooperative_role = 'MEMBER' WHERE cooperative_id IS NOT NULL AND cooperative_role IS NULL"
    )


def downgrade() -> None:
    op.drop_column("users", "cooperative_role")
    cooperative_role_enum.drop(op.get_bind(), checkfirst=True)
