"""Initial schema after manual updates

Revision ID: 1967a8be30f3
Revises: 
Create Date: 2024-10-03 15:25:33.696429

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '1967a8be30f3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the sets table
    op.create_table('sets',
        sa.Column('code', sa.Text(), nullable=False),
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('set_type', sa.Text(), nullable=True),
        sa.Column('card_count', sa.BigInteger(), nullable=True),
        sa.Column('digital', sa.Boolean(), nullable=True),
        sa.Column('foil_only', sa.Boolean(), nullable=True),
        sa.Column('icon_svg_uri', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('code'),
        sa.UniqueConstraint('id')
    )

    # Create the cards table
    op.create_table('cards',
        sa.Column('id', sa.Text(), nullable=False),
        sa.Column('oracle_id', sa.Text(), nullable=True),
        sa.Column('multiverse_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mtgo_id', sa.BigInteger(), nullable=True),
        sa.Column('arena_id', sa.BigInteger(), nullable=True),
        sa.Column('tcgplayer_id', sa.BigInteger(), nullable=True),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('lang', sa.Text(), nullable=True),
        sa.Column('released_at', sa.DateTime(), nullable=True),
        sa.Column('uri', sa.Text(), nullable=True),
        sa.Column('scryfall_uri', sa.Text(), nullable=True),
        sa.Column('layout', sa.Text(), nullable=True),
        sa.Column('highres_image', sa.Boolean(), nullable=True),
        sa.Column('image_status', sa.Text(), nullable=True),
        sa.Column('image_uris', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mana_cost', sa.Text(), nullable=True),
        sa.Column('cmc', sa.Float(), nullable=True),
        sa.Column('type_line', sa.Text(), nullable=True),
        sa.Column('oracle_text', sa.Text(), nullable=True),
        sa.Column('colors', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('color_identity', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('keywords', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('produced_mana', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('legalities', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('games', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reserved', sa.Boolean(), nullable=True),
        sa.Column('foil', sa.Boolean(), nullable=True),
        sa.Column('nonfoil', sa.Boolean(), nullable=True),
        sa.Column('finishes', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('oversized', sa.Boolean(), nullable=True),
        sa.Column('promo', sa.Boolean(), nullable=True),
        sa.Column('full_art', sa.Boolean(), nullable=True),
        sa.Column('textless', sa.Boolean(), nullable=True),
        sa.Column('booster', sa.Boolean(), nullable=True),
        sa.Column('story_spotlight', sa.Boolean(), nullable=True),
        sa.Column('reprint', sa.Boolean(), nullable=True),
        sa.Column('variation', sa.Boolean(), nullable=True),
        sa.Column('set_code', sa.Text(), nullable=True),
        sa.Column('set_name', sa.Text(), nullable=True),
        sa.Column('collector_number', sa.Text(), nullable=False),
        sa.Column('digital', sa.Boolean(), nullable=True),
        sa.Column('rarity', sa.Text(), nullable=True),
        sa.Column('card_back_id', sa.Text(), nullable=True),
        sa.Column('artist', sa.Text(), nullable=True),
        sa.Column('artist_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('illustration_id', sa.Text(), nullable=True),
        sa.Column('border_color', sa.Text(), nullable=True),
        sa.Column('frame', sa.Text(), nullable=True),
        sa.Column('frame_effects', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('prices', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('related_uris', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('purchase_uris', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('promo_types', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('usd_price', sa.Numeric(), nullable=True),
        sa.Column('usd_foil_price', sa.Numeric(), nullable=True),
        sa.Column('quantity_regular', sa.BigInteger(), nullable=True),
        sa.Column('quantity_foil', sa.BigInteger(), nullable=True),
        sa.Column('quantity_kiosk_regular', sa.BigInteger(), nullable=True),
        sa.Column('quantity_kiosk_foil', sa.BigInteger(), nullable=True),
        sa.ForeignKeyConstraint(['set_code'], ['sets.code'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Create indexes
    op.create_index(op.f('ix_cards_name'), 'cards', ['name'], unique=False)
    op.create_index(op.f('ix_cards_oracle_id'), 'cards', ['oracle_id'], unique=False)
    op.create_index(op.f('ix_cards_type_line'), 'cards', ['type_line'], unique=False)

def downgrade():
    # Drop indexes
    op.drop_index(op.f('ix_cards_type_line'), table_name='cards')
    op.drop_index(op.f('ix_cards_oracle_id'), table_name='cards')
    op.drop_index(op.f('ix_cards_name'), table_name='cards')

    # Drop tables
    op.drop_table('cards')
    op.drop_table('sets')
