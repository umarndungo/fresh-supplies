"""store market recommendations on shipments

Revision ID: 20260909_market_recommendations
Revises: 707a3fac1691
"""
from alembic import op
import sqlalchemy as sa


revision = "20260909_market_recommendations"
down_revision = ("0003_add_is_active_to_users", "707a3fac1691")
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("shipments", sa.Column("market_recommendations", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("shipments", "market_recommendations")