"""change released_at to datetime

Revision ID: change_released_at_to_datetime
Revises: c85a075a2a35
Create Date: 2024-09-27 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'change_released_at_to_datetime'
down_revision = 'c85a075a2a35'
branch_labels = None
depends_on = None


def upgrade():
    # Convert released_at from text to datetime
    op.execute("ALTER TABLE sets ALTER COLUMN released_at TYPE TIMESTAMP USING to_timestamp(released_at, 'YYYY-MM-DD')")
    op.execute("ALTER TABLE cards ALTER COLUMN released_at TYPE TIMESTAMP USING to_timestamp(released_at, 'YYYY-MM-DD')")


def downgrade():
    # Convert released_at back to text
    op.execute("ALTER TABLE sets ALTER COLUMN released_at TYPE TEXT USING to_char(released_at, 'YYYY-MM-DD')")
    op.execute("ALTER TABLE cards ALTER COLUMN released_at TYPE TEXT USING to_char(released_at, 'YYYY-MM-DD')")
