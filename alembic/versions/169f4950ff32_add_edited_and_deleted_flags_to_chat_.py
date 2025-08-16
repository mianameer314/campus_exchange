"""add edited and deleted flags to chat_messages

Revision ID: 169f4950ff32
Revises: f08207f3ef27
Create Date: 2025-08-16 16:37:43.072400

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '169f4950ff32'
down_revision: Union[str, Sequence[str], None] = 'f08207f3ef27'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('chat_messages', sa.Column('edited', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column('chat_messages', sa.Column('deleted', sa.Boolean(), nullable=False, server_default=sa.false()))

def downgrade():
    op.drop_column('chat_messages', 'edited')
    op.drop_column('chat_messages', 'deleted')