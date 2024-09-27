"""Update materialized view handling

Revision ID: f4429cfea754
Revises: change_released_at_to_datetime
Create Date: 2024-09-27

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'f4429cfea754'
down_revision = 'change_released_at_to_datetime'
branch_labels = None
depends_on = None


def upgrade():
    # Refresh the materialized view to ensure data consistency
    op.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY set_collection_counts")

    # Drop old indexes no longer needed
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_index('idx_cards_collection_quantities')
        batch_op.drop_index('idx_cards_set_code')

    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.drop_index(
            'idx_sets_relevant_types',
            postgresql_where="(set_type = ANY (ARRAY['core'::text, 'expansion'::text, 'masters'::text, 'draft_innovation'::text, 'funny'::text, 'commander'::text]))"
        )
        batch_op.drop_index('idx_sets_type_released')


def downgrade():
    # Restore old indexes if needed
    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.create_index('idx_sets_type_released', ['set_type', sa.text('released_at DESC')], unique=False)
        batch_op.create_index('idx_sets_relevant_types', [sa.text('released_at DESC')], unique=False, postgresql_where="(set_type = ANY (ARRAY['core'::text, 'expansion'::text, 'masters'::text, 'draft_innovation'::text, 'funny'::text, 'commander'::text]))")

    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.create_index('idx_cards_set_code', ['set_code'], unique=False)
        batch_op.create_index('idx_cards_collection_quantities', ['set_code', 'quantity_collection_regular', 'quantity_collection_foil'], unique=False)

    # Drop the materialized view if needed
    op.execute("DROP MATERIALIZED VIEW IF EXISTS set_collection_counts")
