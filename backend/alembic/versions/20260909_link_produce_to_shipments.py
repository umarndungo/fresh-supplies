"""link shipments to produce lots

Revision ID: 20260909_shipment_produce_link
Revises: 20260909_storage_fields
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260909_shipment_produce_link"
down_revision = "20260909_storage_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shipments", sa.Column("produce_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("shipments", sa.Column("harvest_date_snapshot", sa.DateTime(timezone=True), nullable=True))
    op.add_column("shipments", sa.Column("storage_spoilage_probability_snapshot", sa.Float(), nullable=True))
    op.add_column("shipments", sa.Column("estimated_shelf_life_days_snapshot", sa.Float(), nullable=True))
    op.create_foreign_key("fk_shipments_produce_id", "shipments", "produce", ["produce_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_shipments_produce_id", "shipments", type_="foreignkey")
    op.drop_column("shipments", "estimated_shelf_life_days_snapshot")
    op.drop_column("shipments", "storage_spoilage_probability_snapshot")
    op.drop_column("shipments", "harvest_date_snapshot")
    op.drop_column("shipments", "produce_id")