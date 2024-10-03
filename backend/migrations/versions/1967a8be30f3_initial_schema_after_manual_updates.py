"""Initial schema after manual updates

Revision ID: 1967a8be30f3
Revises:
Create Date: 2024-10-03 15:25:33.696429

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '1967a8be30f3'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the materialized view
    op.execute('''
        CREATE MATERIALIZED VIEW IF NOT EXISTS set_collection_counts AS
        SELECT set_code, 
               SUM(quantity_regular + quantity_foil) as collection_count
        FROM cards
        GROUP BY set_code
    ''')

def downgrade():
    # Drop the materialized view if necessary
    op.execute('DROP MATERIALIZED VIEW IF EXISTS set_collection_counts')
