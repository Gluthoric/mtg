"""Updated quantity fields

Revision ID: a5042ce266ee
Revises: c4c16fcaa592
Create Date: 2024-10-03 09:33:24.638387

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a5042ce266ee'
down_revision = 'c4c16fcaa592'
branch_labels = None
depends_on = None


def upgrade():
    # Drop dependent materialized views before altering the table
    op.execute("DROP MATERIALIZED VIEW IF EXISTS set_collection_counts;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS total_collection_value;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS unique_cards_count;")

    # Add new columns
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_regular', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('quantity_foil', sa.BigInteger(), nullable=True))

    # Migrate data from old columns to new columns
    op.execute("""
    UPDATE cards
    SET
        quantity_regular = quantity_collection_regular,
        quantity_foil = quantity_collection_foil
    """)

    # Drop old columns
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_column('quantity_collection_regular')
        batch_op.drop_column('quantity_collection_foil')

    # Recreate materialized views with updated column names
    op.execute("""
    CREATE MATERIALIZED VIEW set_collection_counts AS
    SELECT
        set_code,
        SUM(quantity_regular + quantity_foil) AS collection_count
    FROM cards
    GROUP BY set_code;
    """)

    op.execute("""
    CREATE MATERIALIZED VIEW total_collection_value AS
    SELECT
        SUM(
            (CAST(prices->>'usd' AS FLOAT) * quantity_regular) +
            (CAST(prices->>'usd_foil' AS FLOAT) * quantity_foil)
        ) AS total_value
    FROM cards;
    """)

    op.execute("""
    CREATE MATERIALIZED VIEW unique_cards_count AS
    SELECT
        COUNT(DISTINCT id) AS unique_cards
    FROM cards
    WHERE quantity_regular > 0 OR quantity_foil > 0;
    """)

def downgrade():
    # Drop materialized views
    op.execute("DROP MATERIALIZED VIEW IF EXISTS set_collection_counts;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS total_collection_value;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS unique_cards_count;")

    # Add old columns back
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_collection_regular', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('quantity_collection_foil', sa.BigInteger(), nullable=True))

    # Migrate data from new columns back to old columns
    op.execute("""
    UPDATE cards
    SET
        quantity_collection_regular = quantity_regular,
        quantity_collection_foil = quantity_foil
    """)

    # Drop new columns
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_column('quantity_regular')
        batch_op.drop_column('quantity_foil')

    # Recreate materialized views with original column names
    op.execute("""
    CREATE MATERIALIZED VIEW set_collection_counts AS
    SELECT
        set_code,
        SUM(quantity_collection_regular + quantity_collection_foil) AS collection_count
    FROM cards
    GROUP BY set_code;
    """)

    op.execute("""
    CREATE MATERIALIZED VIEW total_collection_value AS
    SELECT
        SUM(
            (CAST(prices->>'usd' AS FLOAT) * quantity_collection_regular) +
            (CAST(prices->>'usd_foil' AS FLOAT) * quantity_collection_foil)
        ) AS total_value
    FROM cards;
    """)

    op.execute("""
    CREATE MATERIALIZED VIEW unique_cards_count AS
    SELECT
        COUNT(DISTINCT id) AS unique_cards
    FROM cards
    WHERE quantity_collection_regular > 0 OR quantity_collection_foil > 0;
    """)
