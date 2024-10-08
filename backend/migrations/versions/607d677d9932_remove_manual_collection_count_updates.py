"""Remove manual collection count updates

Revision ID: 607d677d9932
Revises: 1967a8be30f3
Create Date: 2024-10-03 15:53:31.352352

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '607d677d9932'
down_revision = '1967a8be30f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_index('idx_cards_border_color')
        batch_op.drop_index('idx_cards_colors_gin', postgresql_using='gin')
        batch_op.drop_index('idx_cards_frame_effects', postgresql_using='gin')
        batch_op.drop_index('idx_cards_kiosk_inventory', postgresql_where='((quantity_kiosk_regular > 0) OR (quantity_kiosk_foil > 0))')
        batch_op.drop_index('idx_cards_name_trgm', postgresql_using='gin')
        batch_op.drop_index('idx_cards_prices_usd')
        batch_op.drop_index('idx_cards_prices_usd_foil')
        batch_op.drop_index('idx_cards_promo_types', postgresql_using='gin')
        batch_op.drop_index('idx_cards_search', postgresql_using='gin')
        batch_op.drop_index('idx_cards_search_vector', postgresql_using='gin')
        batch_op.drop_index('idx_cards_set_collection')
        batch_op.drop_index('idx_cards_type_line_trgm', postgresql_using='gin')
        batch_op.drop_column('search_vector')
        batch_op.drop_column('set_id')

    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.drop_index('idx_sets_code')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('sets', schema=None) as batch_op:
        batch_op.create_index('idx_sets_code', ['code'], unique=True)

    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('set_id', sa.UUID(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('search_vector', postgresql.TSVECTOR(), autoincrement=False, nullable=True))
        batch_op.create_index('idx_cards_type_line_trgm', ['type_line'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_set_collection', ['set_code', 'name'], unique=False)
        batch_op.create_index('idx_cards_search_vector', ['search_vector'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_search', [sa.text("to_tsvector('english'::regconfig, (name || ' '::text) || type_line)")], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_promo_types', ['promo_types'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_prices_usd_foil', [sa.text("(prices ->> 'usd_foil'::text)")], unique=False)
        batch_op.create_index('idx_cards_prices_usd', [sa.text("(prices ->> 'usd'::text)")], unique=False)
        batch_op.create_index('idx_cards_name_trgm', ['name'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_kiosk_inventory', ['id'], unique=False, postgresql_where='((quantity_kiosk_regular > 0) OR (quantity_kiosk_foil > 0))')
        batch_op.create_index('idx_cards_frame_effects', ['frame_effects'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_colors_gin', ['colors'], unique=False, postgresql_using='gin')
        batch_op.create_index('idx_cards_border_color', ['border_color'], unique=False)

    # ### end Alembic commands ###
