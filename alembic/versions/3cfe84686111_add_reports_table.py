"""add reports table

Revision ID: 3cfe84686111
Revises: 169f4950ff32
Create Date: 2025-08-17 12:48:35.994146

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3cfe84686111'
down_revision: Union[str, Sequence[str], None] = '169f4950ff32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "reports",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("reporter_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reported_listing_id", sa.Integer(), sa.ForeignKey("listings.id"), nullable=True),
        sa.Column("reported_user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("status", sa.Enum("PENDING", "REVIEWED", "REJECTED", "RESOLVED", name="reportstatus"), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("reviewed_by", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("audit_log", sa.Text(), nullable=True)
    )

def downgrade():
    op.drop_table("reports")