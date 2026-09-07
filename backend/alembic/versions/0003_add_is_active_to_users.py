"""add is_active to users

Revision ID: 0003_add_is_active_to_users
Revises: 105b70ab3102
Create Date: 2026-09-07 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = '0003_add_is_active_to_users'
down_revision = '105b70ab3102'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        'users',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
    )


def downgrade() -> None:
    op.drop_column('users', 'is_active')