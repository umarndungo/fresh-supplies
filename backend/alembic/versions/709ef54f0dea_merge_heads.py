"""merge heads

Revision ID: 709ef54f0dea
Revises: 0001_add_commodity_class, 0002_mobile_api
Create Date: 2026-09-05 16:50:52.247310

"""
from alembic import op
import sqlalchemy as sa


revision = '709ef54f0dea'
down_revision = ('0001_add_commodity_class', '0002_mobile_api')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
