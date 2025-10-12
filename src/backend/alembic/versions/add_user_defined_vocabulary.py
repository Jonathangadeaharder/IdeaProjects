"""add user_defined vocabulary support

Revision ID: b4c7d2f9e1a3
Revises: acbddef5428e
Create Date: 2025-10-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b4c7d2f9e1a3'
down_revision: Union[str, Sequence[str], None] = 'make_vocab_id_nullable'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add user_id column to vocabulary_words to support user-defined vocabulary."""
    # SQLite doesn't support adding foreign keys via ALTER, so we use batch mode
    with op.batch_alter_table('vocabulary_words', schema=None) as batch_op:
        # Add user_id column (nullable, FK to users)
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))

        # Drop old unique constraint
        batch_op.drop_constraint('uq_vocabulary_word_lang', type_='unique')

        # Create new unique constraint including user_id
        batch_op.create_unique_constraint('uq_vocabulary_word_lang_user', ['word', 'language', 'user_id'])

        # Add foreign key
        batch_op.create_foreign_key('fk_vocabulary_words_user_id', 'users', ['user_id'], ['id'], ondelete='CASCADE')

        # Add index on user_id for efficient queries
        batch_op.create_index('idx_vocabulary_user', ['user_id'])


def downgrade() -> None:
    """Remove user_id column and revert to original schema."""
    # SQLite doesn't support dropping foreign keys via ALTER, so we use batch mode
    with op.batch_alter_table('vocabulary_words', schema=None) as batch_op:
        # Drop new index
        batch_op.drop_index('idx_vocabulary_user')

        # Drop foreign key
        batch_op.drop_constraint('fk_vocabulary_words_user_id', type_='foreignkey')

        # Drop new unique constraint
        batch_op.drop_constraint('uq_vocabulary_word_lang_user', type_='unique')

        # Recreate original unique constraint
        batch_op.create_unique_constraint('uq_vocabulary_word_lang', ['word', 'language'])

        # Drop column
        batch_op.drop_column('user_id')
