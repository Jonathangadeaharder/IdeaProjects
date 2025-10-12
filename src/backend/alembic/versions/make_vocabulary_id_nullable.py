"""make vocabulary_id nullable to support marking unknown words as known

Revision ID: make_vocab_id_nullable
Revises: acbddef5428e
Create Date: 2025-10-06 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'make_vocab_id_nullable'
down_revision = 'acbddef5428e'
branch_labels = None
depends_on = None


def upgrade():
    """
    Make vocabulary_id nullable in user_vocabulary_progress table.

    This allows users to mark words as known even if they're not in the
    main vocabulary database. The lemma field serves as the primary
    identifier for filtering known words.

    Uses batch mode for SQLite compatibility.
    """
    # Step 1: Clean up duplicates before adding unique constraint
    # Keep the row with the highest confidence_level for each (user_id, lemma, language)
    conn = op.get_bind()
    conn.execute(sa.text("""
        DELETE FROM user_vocabulary_progress
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM user_vocabulary_progress
            GROUP BY user_id, lemma, language
            HAVING MAX(confidence_level) = confidence_level
        )
    """))

    # Step 2: Use batch mode for SQLite compatibility
    with op.batch_alter_table('user_vocabulary_progress', schema=None) as batch_op:
        # Drop the old unique constraint
        batch_op.drop_constraint('uq_user_vocabulary', type_='unique')

        # Make vocabulary_id nullable
        batch_op.alter_column('vocabulary_id',
                              existing_type=sa.Integer(),
                              nullable=True)

        # Add new unique constraint on (user_id, lemma, language)
        batch_op.create_unique_constraint(
            'uq_user_lemma_language',
            ['user_id', 'lemma', 'language']
        )


def downgrade():
    """Revert changes"""
    with op.batch_alter_table('user_vocabulary_progress', schema=None) as batch_op:
        # Drop the new unique constraint
        batch_op.drop_constraint('uq_user_lemma_language', type_='unique')

        # Make vocabulary_id non-nullable again (this will fail if any NULL values exist)
        batch_op.alter_column('vocabulary_id',
                              existing_type=sa.Integer(),
                              nullable=False)

        # Restore original unique constraint
        batch_op.create_unique_constraint(
            'uq_user_vocabulary',
            ['user_id', 'vocabulary_id']
        )
