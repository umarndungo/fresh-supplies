"""initial schema

Revision ID: 0000_initial
Revises:
Create Date: 2026-09-01

Creates the base schema (users, shipments, produce) including the
commodity_class column on produce so a fresh database can be built entirely
with `alembic upgrade head`.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0000_initial"
down_revision = None
branch_labels = None
depends_on = None

user_role = postgresql.ENUM(
    "ADMINISTRATOR", "LOGISTICS_MANAGER", "FARMER_COOPERATIVE", "MARKET_ANALYST",
    name="user_role", create_type=False,
)
shipment_status = postgresql.ENUM(
    "SCHEDULED", "IN_TRANSIT", "DELIVERED", "CANCELLED",
    name="shipment_status", create_type=False,
)
produce_status = postgresql.ENUM(
    "AVAILABLE", "RESERVED", "SHIPPED", "SPOILED",
    name="produce_status", create_type=False,
)
commodity_class = postgresql.ENUM(
    "PERISHABLE", "STAPLE", name="commodity_class", create_type=False,
)


def upgrade() -> None:
    for enum in (user_role, shipment_status, produce_status, commodity_class):
        enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False),
        sa.Column("organization_name", sa.String(255), nullable=True),
        sa.Column("avatar_url", sa.String(512), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "shipments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("origin", sa.String(255), nullable=False),
        sa.Column("destination", sa.String(255), nullable=False),
        sa.Column("produce_type", sa.String(255), nullable=False),
        sa.Column("status", shipment_status, nullable=False),
        sa.Column("scheduled_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("delivery_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "produce",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("variety", sa.String(255), nullable=False),
        sa.Column("quantity_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quality_grade", sa.String(50), nullable=False),
        sa.Column("harvest_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("storage_location", sa.String(255), nullable=False),
        sa.Column("commodity_class", commodity_class, nullable=False),
        sa.Column("cooperative_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", produce_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("produce")
    op.drop_table("shipments")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    for enum in (user_role, shipment_status, produce_status, commodity_class):
        enum.drop(op.get_bind(), checkfirst=True)
