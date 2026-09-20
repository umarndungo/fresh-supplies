"""add storage freshness fields to produce

Revision ID: 20260909_storage_fields
Revises: 20260909_market_recommendations
"""
from alembic import op
import sqlalchemy as sa


revision = "20260909_storage_fields"
down_revision = "20260909_market_recommendations"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("produce", sa.Column("storage_temperature_c", sa.Float(), nullable=True))
    op.add_column("produce", sa.Column("storage_pressure_psi", sa.Float(), nullable=True))
    op.add_column("produce", sa.Column("storage_spoilage_probability", sa.Float(), nullable=True))
    op.add_column("produce", sa.Column("storage_risk_tier", sa.String(length=20), nullable=True))
    op.add_column("produce", sa.Column("storage_spoil_prediction", sa.Boolean(), nullable=True))
    op.add_column("produce", sa.Column("estimated_shelf_life_days", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("produce", "estimated_shelf_life_days")
    op.drop_column("produce", "storage_spoil_prediction")
    op.drop_column("produce", "storage_risk_tier")
    op.drop_column("produce", "storage_spoilage_probability")
    op.drop_column("produce", "storage_pressure_psi")
    op.drop_column("produce", "storage_temperature_c")