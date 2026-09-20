"""widen otp_codes.phone_number into a generic email-capable identifier

Revision ID: 20260918_otp_email_identifier
Revises: 20260918_driver_role

Mobile login OTP switches from phone number to email (per product
decision). phone_number was VARCHAR(20) — too short for an email address —
so this renames it to `identifier` and widens it to VARCHAR(255). The
column's actual content is unaffected; only new OTP rows going forward will
contain emails instead of phone numbers.
"""
from alembic import op
import sqlalchemy as sa

revision = "20260918_otp_email_identifier"
down_revision = "20260918_driver_role"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column("otp_codes", "phone_number", new_column_name="identifier", type_=sa.String(255))


def downgrade() -> None:
    op.alter_column("otp_codes", "identifier", new_column_name="phone_number", type_=sa.String(20))
