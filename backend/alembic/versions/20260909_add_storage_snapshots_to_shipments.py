"""add storage condition snapshots to shipments

Revision ID: 20260909_storage_snapshots
Revises: 20260909_shipment_produce_link
"""
from alembic import op
import sqlalchemy as sa


revision = "20260909_storage_snapshots"
down_revision = "20260909_shipment_produce_link"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shipments", sa.Column("storage_temperature_c_snapshot", sa.Float(), nullable=True))
    op.add_column("shipments", sa.Column("storage_pressure_psi_snapshot", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("shipments", "storage_pressure_psi_snapshot")
    op.drop_column("shipments", "storage_temperature_c_snapshot")