"""fix produce tenancy: add owner_type/created_by, repoint cooperative_id at cooperatives

Revision ID: 20260918_produce_tenant_fields
Revises: 20260909_storage_snapshots

`produce.cooperative_id` was a mislabeled FK to users.id, actually holding
the creator's own user id (see produce_service.create_produce, pre-fix:
`cooperative_id=actor.id`). This migration adds real `owner_type` +
`created_by` columns, backfills them from that mislabeled column, and
repoints `cooperative_id` at the real `cooperatives` table (NULL for
individual/solo tenants) — see backend/docs/multitenancy_design.md §2.1.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "20260918_produce_tenant_fields"
down_revision = "20260909_storage_snapshots"
branch_labels = None
depends_on = None

owner_type_enum = postgresql.ENUM(
    "COOPERATIVE", "INDIVIDUAL", name="owner_type_enum", create_type=False,
)


def upgrade() -> None:
    op.add_column("produce", sa.Column("owner_type", owner_type_enum, nullable=True))
    op.add_column("produce", sa.Column("created_by", postgresql.UUID(as_uuid=True), nullable=True))

    # Recover the real creator from the mislabeled cooperative_id.
    op.execute("UPDATE produce SET created_by = cooperative_id")

    # Derive owner_type from the creator's own account_type (mirrors the
    # mobile shipment path's existing logic in mobile_shipment_service.py).
    # account_type_enum and owner_type_enum are distinct Postgres enum types
    # even though they share the same labels — Postgres won't implicitly
    # cast between them, so go via text explicitly.
    op.execute(
        """
        UPDATE produce p
        SET owner_type = COALESCE(u.account_type::text, 'INDIVIDUAL')::owner_type_enum
        FROM users u
        WHERE u.id = p.created_by
        """
    )

    # Re-point cooperative_id at the creator's actual cooperative.
    op.execute(
        """
        UPDATE produce p
        SET cooperative_id = u.cooperative_id
        FROM users u
        WHERE u.id = p.created_by AND p.owner_type = 'COOPERATIVE' AND u.cooperative_id IS NOT NULL
        """
    )
    op.execute("UPDATE produce SET cooperative_id = NULL WHERE owner_type = 'INDIVIDUAL'")

    # Defensive: a COOPERATIVE-type creator whose own cooperative_id is
    # somehow NULL would otherwise leave produce.cooperative_id dangling
    # against the new FK — degrade those rows to INDIVIDUAL instead of
    # leaving an inconsistent reference.
    op.execute(
        "UPDATE produce SET owner_type = 'INDIVIDUAL' WHERE owner_type = 'COOPERATIVE' AND cooperative_id IS NULL"
    )

    op.drop_constraint("produce_cooperative_id_fkey", "produce", type_="foreignkey")
    op.create_foreign_key(
        "produce_cooperative_id_fkey", "produce", "cooperatives", ["cooperative_id"], ["id"]
    )
    op.create_foreign_key("fk_produce_created_by", "produce", "users", ["created_by"], ["id"])

    op.alter_column("produce", "cooperative_id", nullable=True)
    op.alter_column("produce", "owner_type", nullable=False)
    op.alter_column("produce", "created_by", nullable=False)


def downgrade() -> None:
    op.drop_constraint("fk_produce_created_by", "produce", type_="foreignkey")
    op.drop_constraint("produce_cooperative_id_fkey", "produce", type_="foreignkey")

    # Restore pre-migration semantics: cooperative_id holds the creator id.
    op.execute("UPDATE produce SET cooperative_id = created_by")
    op.create_foreign_key("produce_cooperative_id_fkey", "produce", "users", ["cooperative_id"], ["id"])
    op.alter_column("produce", "cooperative_id", nullable=False)

    op.drop_column("produce", "created_by")
    op.drop_column("produce", "owner_type")
