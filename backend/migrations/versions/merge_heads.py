"""Merge heads

Revision ID: b3f9a7c9e7d0
Revises: 8e2b95fa81fb, rplc_set_coll_view
Create Date: 2024-10-03 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'b3f9a7c9e7d0'
down_revision = ('8e2b95fa81fb', 'rplc_set_coll_view')
branch_labels = None
depends_on = None

def upgrade():
    pass

def downgrade():
    pass
