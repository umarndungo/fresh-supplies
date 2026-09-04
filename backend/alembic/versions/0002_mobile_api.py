"""mobile api schema

Revision ID: 0002_mobile_api
Revises: 0000_initial
Create Date: 2026-09-04

Adds cooperative, OTP, shipment-sync-staging, and device-token tables.
Extends users and shipments with mobile-API columns and PG enums.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0002_mobile_api"
down_revision = "0000_initial"
branch_labels = None
depends_on = None

account_type_enum = postgresql.ENUM(
    "COOPERATIVE", "INDIVIDUAL", name="account_type_enum", create_type=False,
)
owner_type_enum = postgresql.ENUM(
    "COOPERATIVE", "INDIVIDUAL", name="owner_type_enum", create_type=False,
)
reconciliation_status_enum = postgresql.ENUM(
    "PENDING", "RECONCILED", "FAILED", name="reconciliation_status_enum", create_type=False,
)


def upgrade() -> None:
    for enum in (account_type_enum, owner_type_enum, reconciliation_status_enum):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "cooperatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )

    op.create_table(
        "otp_codes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("code", sa.String(6), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_otp_codes_phone_number", "otp_codes", ["phone_number"])

    op.create_table(
        "shipment_sync_staging",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("client_id", sa.String(36), nullable=False),
        sa.Column("crop", sa.String(255), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("location_lat", sa.Float(), nullable=False),
        sa.Column("location_lon", sa.Float(), nullable=False),
        sa.Column("photo_ref", sa.String(512), nullable=True),
        sa.Column("photo_status", sa.String(20), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("owner_type", owner_type_enum, nullable=False),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cooperatives.id"), nullable=True),
        sa.Column("submitted_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("sync_received_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("reconciliation_status", reconciliation_status_enum, nullable=False),
        sa.Column("reconciled_shipment_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("shipments.id"), nullable=True),
    )
    op.create_index("ix_shipment_sync_staging_client_id", "shipment_sync_staging", ["client_id"], unique=True)

    op.create_table(
        "device_tokens",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("device_token", sa.String(512), nullable=False),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_device_tokens_user_id", "device_tokens", ["user_id"])

    op.add_column("users", sa.Column("phone_number", sa.String(20), nullable=True))
    op.create_unique_constraint("uq_users_phone_number", "users", ["phone_number"])
    op.add_column("users", sa.Column("account_type", account_type_enum, nullable=True))
    op.add_column("users", sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cooperatives.id"), nullable=True))
    op.add_column("users", sa.Column("phone_verified", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("users", sa.Column("profile_completed", sa.Boolean(), nullable=False, server_default=sa.text("false")))

    op.add_column("shipments", sa.Column("owner_type", owner_type_enum, nullable=True))
    op.add_column("shipments", sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cooperatives.id"), nullable=True))
    op.add_column("shipments", sa.Column("submitted_by_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True))
    op.add_column("shipments", sa.Column("photo_ref", sa.String(512), nullable=True))
    op.add_column("shipments", sa.Column("photo_status", sa.String(20), nullable=True))
    op.add_column("shipments", sa.Column("client_id", sa.String(36), nullable=True))
    op.create_unique_constraint("uq_shipments_client_id", "shipments", ["client_id"])


def downgrade() -> None:
    op.drop_constraint("uq_shipments_client_id", "shipments", type_="unique")
    op.drop_column("shipments", "client_id")
    op.drop_column("shipments", "photo_status")
    op.drop_column("shipments", "photo_ref")
    op.drop_column("shipments", "submitted_by_user_id")
    op.drop_column("shipments", "cooperative_id")
    op.drop_column("shipments", "owner_type")

    op.drop_column("users", "profile_completed")
    op.drop_column("users", "phone_verified")
    op.drop_column("users", "cooperative_id")
    op.drop_column("users", "account_type")
    op.drop_constraint("uq_users_phone_number", "users", type_="unique")
    op.drop_column("users", "phone_number")

    op.drop_table("device_tokens")
    op.drop_table("shipment_sync_staging")
    op.drop_table("otp_codes")
    op.drop_table("cooperatives")

    for enum in (reconciliation_status_enum, owner_type_enum, account_type_enum):
        enum.drop(op.get_bind(), checkfirst=True)
