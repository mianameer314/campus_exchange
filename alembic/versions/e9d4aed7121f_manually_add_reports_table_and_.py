"""Manually add reports table and reportstatus enum

Revision ID: e9d4aed7121f
Revises: 3cfe84686111
Create Date: 2025-08-17 13:15:04.772498
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'e9d4aed7121f'
down_revision = '3cfe84686111'
branch_labels = None
depends_on = None

# Define enum type globally with create_type=False when used in table
reportstatus = postgresql.ENUM(
    'PENDING', 'REVIEWED', 'REJECTED', 'RESOLVED',
    name='reportstatus',
    create_type=False  # Important! DON'T create enum here
)

def upgrade():
    # Create enum type if not exists (only this line creates the type)
    op.execute("""
    DO $$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reportstatus') THEN
            CREATE TYPE reportstatus AS ENUM ('PENDING', 'REVIEWED', 'REJECTED', 'RESOLVED');
        END IF;
    END$$;
    """)

    # Create reports table referencing the existing enum type (won't recreate enum)
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('reporter_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('reported_listing_id', sa.Integer, sa.ForeignKey('listings.id'), nullable=True),
        sa.Column('reported_user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reason', sa.Text, nullable=False),
        sa.Column('status', reportstatus, nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('reviewed_by', sa.Integer, sa.ForeignKey('users.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('audit_log', sa.Text, nullable=True),
    )

def downgrade():
    # Drop reports table
    op.drop_table('reports')

    # Drop enum type safely if unused
    op.execute("""
    DO $$
    BEGIN
        IF EXISTS (SELECT 1 FROM pg_type WHERE typname = 'reportstatus') THEN
            DROP TYPE reportstatus;
        END IF;
    END$$;
    """)
