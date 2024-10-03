"""Replace set_collection_counts table with materialized view

Revision ID: rplc_set_coll_view
Revises: 1967a8be30f3
Create Date: 2024-10-03 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'rplc_set_coll_view'
down_revision = '1967a8be30f3'
branch_labels = None
depends_on = None

def upgrade():
    # Drop the existing table
    op.drop_table('set_collection_counts')

    # Create the materialized view
    op.execute('''
        CREATE MATERIALIZED VIEW set_collection_counts AS
        SELECT set_code,
               SUM(quantity_regular + quantity_foil) as collection_count
        FROM cards
        GROUP BY set_code
    ''')

def downgrade():
    # Drop the materialized view
    op.execute('DROP MATERIALIZED VIEW IF EXISTS set_collection_counts')

    # Recreate the table
    op.create_table('set_collection_counts',
        sa.Column('set_code', sa.Text(), nullable=False),
        sa.Column('collection_count', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['set_code'], ['sets.code']),
        sa.PrimaryKeyConstraint('set_code')
    )
