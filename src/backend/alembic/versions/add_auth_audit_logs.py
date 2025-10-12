"""add auth audit logs table

Revision ID: auth_audit_logs
Revises: refresh_token_families
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'auth_audit_logs'
down_revision = 'refresh_token_families'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create auth_audit_logs table for security monitoring"""
    op.create_table(
        'auth_audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_detail', sa.Text(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes for performance
    op.create_index('idx_audit_user_id', 'auth_audit_logs', ['user_id'])
    op.create_index('idx_audit_event_type', 'auth_audit_logs', ['event_type'])
    op.create_index('idx_audit_timestamp', 'auth_audit_logs', ['timestamp'])
    op.create_index('idx_audit_success', 'auth_audit_logs', ['success'])

    # Composite index for user history queries
    op.create_index('idx_audit_user_timestamp', 'auth_audit_logs', ['user_id', 'timestamp'])


def downgrade() -> None:
    """Drop auth_audit_logs table"""
    op.drop_index('idx_audit_user_timestamp', table_name='auth_audit_logs')
    op.drop_index('idx_audit_success', table_name='auth_audit_logs')
    op.drop_index('idx_audit_timestamp', table_name='auth_audit_logs')
    op.drop_index('idx_audit_event_type', table_name='auth_audit_logs')
    op.drop_index('idx_audit_user_id', table_name='auth_audit_logs')
    op.drop_table('auth_audit_logs')
