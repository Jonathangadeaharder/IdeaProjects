"""add native_language and target_language to users

Revision ID: acbddef5428e
Revises: 0b9cb76a1e84
Create Date: 2025-10-03 13:31:02.398859

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'acbddef5428e'
down_revision: Union[str, Sequence[str], None] = '0b9cb76a1e84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add native_language and target_language columns to users table."""
    op.add_column('users', sa.Column('native_language', sa.String(5), server_default='en', nullable=False))
    op.add_column('users', sa.Column('target_language', sa.String(5), server_default='de', nullable=False))


def downgrade() -> None:
    """Remove native_language and target_language columns from users table."""
    op.drop_column('users', 'target_language')
    op.drop_column('users', 'native_language')
