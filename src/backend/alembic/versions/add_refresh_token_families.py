"""add refresh token families table

Revision ID: refresh_token_families
Revises: b4c7d2f9e1a3
Create Date: 2025-10-09

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = 'refresh_token_families'
down_revision = 'b4c7d2f9e1a3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create refresh_token_families table for token rotation"""
    op.create_table(
        'refresh_token_families',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('family_id', sa.String(length=64), nullable=False),
        sa.Column('token_hash', sa.String(length=128), nullable=False),
        sa.Column('generation', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=func.now()),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_reason', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )

    # Create indexes for performance
    op.create_index('idx_token_family_user_id', 'refresh_token_families', ['user_id'])
    op.create_index('idx_token_family_expires', 'refresh_token_families', ['expires_at'])
    op.create_index('idx_token_family_revoked', 'refresh_token_families', ['is_revoked'])

    # Unique indexes for token lookup and family tracking
    op.create_index(op.f('ix_refresh_token_families_family_id'), 'refresh_token_families', ['family_id'], unique=True)
    op.create_index(op.f('ix_refresh_token_families_token_hash'), 'refresh_token_families', ['token_hash'], unique=True)


def downgrade() -> None:
    """Drop refresh_token_families table"""
    op.drop_index(op.f('ix_refresh_token_families_token_hash'), table_name='refresh_token_families')
    op.drop_index(op.f('ix_refresh_token_families_family_id'), table_name='refresh_token_families')
    op.drop_index('idx_token_family_revoked', table_name='refresh_token_families')
    op.drop_index('idx_token_family_expires', table_name='refresh_token_families')
    op.drop_index('idx_token_family_user_id', table_name='refresh_token_families')
    op.drop_table('refresh_token_families')
