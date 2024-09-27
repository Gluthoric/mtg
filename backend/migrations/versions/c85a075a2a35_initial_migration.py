"""Initial migration

Revision ID: c85a075a2a35
Revises:
Create Date: 2024-09-26 21:53:39.735867

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'c85a075a2a35'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Alter the 'sets' table
    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.alter_column('id', existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column('code', existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column('name', existing_type=sa.TEXT(), nullable=False)

        # Ensure 'code' is unique before creating foreign key
        batch_op.create_index(batch_op.f('ix_sets_code'), ['code'], unique=True)

        # Drop unnecessary indexes
        batch_op.drop_index('idx_sets_code_unique')
        batch_op.drop_index('idx_sets_name_trgm', postgresql_using='gin')
        batch_op.drop_index('idx_sets_released_at')
        batch_op.drop_index('idx_sets_set_type')

    # Alter the 'cards' table
    with op.batch_alter_table('cards', schema=None) as batch_op:
        # Add new columns with default empty JSON
        batch_op.add_column(sa.Column('frame_effects', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
        batch_op.add_column(sa.Column('promo_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True, server_default='[]'))
        
        # Altering columns from TEXT to JSONB with proper USING clause and removing server default
        batch_op.alter_column('multiverse_ids',
                              existing_type=sa.TEXT(),
                              type_=postgresql.JSONB(astext_type=sa.Text()),
                              existing_nullable=True,
                              postgresql_using="CASE WHEN multiverse_ids IS NULL THEN '[]'::jsonb ELSE multiverse_ids::jsonb END")
        
        batch_op.alter_column('purchase_uris',
                              existing_type=sa.TEXT(),
                              type_=postgresql.JSONB(astext_type=sa.Text()),
                              existing_nullable=True,
                              postgresql_using="CASE WHEN purchase_uris IS NULL THEN '{}'::jsonb ELSE purchase_uris::jsonb END")
        
        # Remove server defaults after data migration
        batch_op.alter_column('frame_effects',
                              server_default=None)
        batch_op.alter_column('promo_types',
                              server_default=None)
        
        # Other column updates
        batch_op.alter_column('name', existing_type=sa.TEXT(), nullable=False)
        batch_op.alter_column('collector_number', existing_type=sa.TEXT(), nullable=False)

        # Drop and recreate indexes
        batch_op.drop_index('idx_cards_collector_number')
        batch_op.drop_index('idx_cards_colors_gin', postgresql_using='gin')
        batch_op.drop_index('idx_cards_name_trgm', postgresql_using='gin')
        batch_op.drop_index('idx_cards_prices', postgresql_using='gin')
        batch_op.drop_index('idx_cards_rarity')
        batch_op.drop_index('idx_cards_set_code')
        batch_op.drop_index('idx_cards_set_code_rarity')
        batch_op.drop_index('idx_cards_set_code_released_at')
        batch_op.drop_index('idx_cards_usd_foil_price')
        batch_op.drop_index('idx_cards_usd_price')

        # Recreate necessary indexes
        batch_op.create_index(batch_op.f('ix_cards_name'), ['name'], unique=False)
        batch_op.create_index(batch_op.f('ix_cards_oracle_id'), ['oracle_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_cards_rarity'), ['rarity'], unique=False)
        batch_op.create_index(batch_op.f('ix_cards_set_code'), ['set_code'], unique=False)
        batch_op.create_index(batch_op.f('ix_cards_type_line'), ['type_line'], unique=False)

        # Create foreign key after ensuring 'code' is unique in 'sets'
        batch_op.create_foreign_key(None, 'sets', ['set_code'], ['code'])

        # Keep 'usd_price' and 'usd_foil_price' columns
        batch_op.alter_column('usd_price', existing_type=sa.NUMERIC(), nullable=True)
        batch_op.alter_column('usd_foil_price', existing_type=sa.NUMERIC(), nullable=True)

def downgrade():
    # Downgrade for 'sets' table
    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_sets_code'))
        batch_op.create_index('idx_sets_set_type', ['set_type'], unique=False)
        batch_op.create_index('idx_sets_released_at', ['released_at'], unique=False)
        batch_op.create_index('idx_sets_name_trgm', ['name'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_sets_code_unique', ['code'], unique=True)
        batch_op.alter_column('name', existing_type=sa.TEXT(), nullable=True)
        batch_op.alter_column('code', existing_type=sa.TEXT(), nullable=True)
        batch_op.alter_column('id', existing_type=sa.TEXT(), nullable=True)

    # Downgrade for 'cards' table
    with op.batch_alter_table('cards', schema=None) as batch_op:
        # Drop new columns
        batch_op.drop_column('promo_types')
        batch_op.drop_column('frame_effects')

        # Drop foreign key constraint
        batch_op.drop_constraint(None, type_='foreignkey')

        # Drop new indexes and recreate original ones
        batch_op.drop_index(batch_op.f('ix_cards_type_line'))
        batch_op.drop_index(batch_op.f('ix_cards_set_code'))
        batch_op.drop_index(batch_op.f('ix_cards_rarity'))
        batch_op.drop_index(batch_op.f('ix_cards_oracle_id'))
        batch_op.drop_index(batch_op.f('ix_cards_name'))

        batch_op.create_index('idx_cards_usd_price', ['usd_price'], unique=False)
        batch_op.create_index('idx_cards_usd_foil_price', ['usd_foil_price'], unique=False)
        batch_op.create_index('idx_cards_set_code_released_at', ['set_code', sa.text('released_at DESC')], unique=False)
        batch_op.create_index('idx_cards_set_code_rarity', ['set_code', 'rarity'], unique=False)
        batch_op.create_index('idx_cards_set_code', ['set_code'], unique=False)
        batch_op.create_index('idx_cards_rarity', ['rarity'], unique=False)
        batch_op.create_index('idx_cards_prices', ['prices'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_name_trgm', ['name'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_colors_gin', ['colors'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_collector_number', ['set_code', 'collector_number'], unique=False)

        # Revert JSONB columns back to TEXT
        batch_op.alter_column('purchase_uris',
                              existing_type=postgresql.JSONB(astext_type=sa.Text()),
                              type_=sa.TEXT(),
                              existing_nullable=True)
        batch_op.alter_column('multiverse_ids',
                              existing_type=postgresql.JSONB(astext_type=sa.Text()),
                              type_=sa.TEXT(),
                              existing_nullable=True)

        # Revert other column updates
        batch_op.alter_column('name', existing_type=sa.TEXT(), nullable=True)
        batch_op.alter_column('collector_number', existing_type=sa.TEXT(), nullable=True)

