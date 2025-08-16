"""create blocked_users table

Revision ID: f08207f3ef27
Revises: 9fd757dfd3bb
Create Date: 2025-08-16 16:36:28.505328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f08207f3ef27'
down_revision: Union[str, Sequence[str], None] = '9fd757dfd3bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        'blocked_users',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('blocked_by', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('user_id', 'blocked_by', name='uq_user_blocked_by')
    )

def downgrade():
    op.drop_table('blocked_users')