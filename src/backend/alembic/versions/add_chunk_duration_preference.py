"""add chunk duration preference

Revision ID: add_chunk_duration
Revises: auth_audit_logs
Create Date: 2025-10-15 20:10:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_chunk_duration'
down_revision = 'auth_audit_logs'
branch_labels = None
depends_on = None


def upgrade():
    # Add chunk_duration_minutes column with default value of 20
    op.add_column('users', sa.Column('chunk_duration_minutes', sa.Integer(), nullable=False, server_default='20'))


def downgrade():
    # Remove chunk_duration_minutes column
    op.drop_column('users', 'chunk_duration_minutes')
