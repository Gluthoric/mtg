"""Updated quantity fields

Revision ID: a5042ce266ee
Revises: c4c16fcaa592
Create Date: 2024-10-03 09:33:24.638387

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import logging

# revision identifiers, used by Alembic.
revision = 'a5042ce266ee'
down_revision = 'c4c16fcaa592'
branch_labels = None
depends_on = None

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def upgrade():
    logger.info("Starting upgrade process")
    
    # Drop dependent materialized views before altering the table
    logger.info("Dropping materialized views")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS set_collection_counts;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS total_collection_value;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS unique_cards_count;")

    # Add new columns
    logger.info("Adding new columns")
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_regular', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('quantity_foil', sa.BigInteger(), nullable=True))

    # Migrate data from old columns to new columns
    logger.info("Migrating data to new columns")
    op.execute("""
    UPDATE cards
    SET
        quantity_regular = quantity_collection_regular,
        quantity_foil = quantity_collection_foil
    """)

    # Drop old columns
    logger.info("Dropping old columns")
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_column('quantity_collection_regular')
        batch_op.drop_column('quantity_collection_foil')

    # Create set_collection_counts materialized view
    logger.info("Creating set_collection_counts materialized view")
    op.execute("""
    CREATE MATERIALIZED VIEW set_collection_counts AS
    SELECT
        set_code,
        COALESCE(SUM(quantity_regular + quantity_foil), 0) AS collection_count
    FROM cards
    GROUP BY set_code;
    """)
    
    # Create a unique index on set_code for faster lookups
    logger.info("Creating index on set_collection_counts")
    op.execute("CREATE UNIQUE INDEX ON set_collection_counts (set_code);")

    logger.info("Creating total_collection_value materialized view")
    op.execute("""
    CREATE MATERIALIZED VIEW total_collection_value AS
    SELECT
        SUM(
            (CAST(prices->>'usd' AS FLOAT) * quantity_regular) +
            (CAST(prices->>'usd_foil' AS FLOAT) * quantity_foil)
        ) AS total_value
    FROM cards;
    """)

    logger.info("Creating unique_cards_count materialized view")
    op.execute("""
    CREATE MATERIALIZED VIEW unique_cards_count AS
    SELECT
        COUNT(DISTINCT id) AS unique_cards
    FROM cards
    WHERE quantity_regular > 0 OR quantity_foil > 0;
    """)

    logger.info("Upgrade process completed")

def downgrade():
    logger.info("Starting downgrade process")

    # Drop dependent materialized views
    logger.info("Dropping materialized views")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS set_collection_counts;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS total_collection_value;")
    op.execute("DROP MATERIALIZED VIEW IF EXISTS unique_cards_count;")

    # Add old columns back
    logger.info("Adding old columns back")
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.add_column(sa.Column('quantity_collection_regular', sa.BigInteger(), nullable=True))
        batch_op.add_column(sa.Column('quantity_collection_foil', sa.BigInteger(), nullable=True))

    # Migrate data from new columns back to old columns
    logger.info("Migrating data back to old columns")
    op.execute("""
    UPDATE cards
    SET
        quantity_collection_regular = COALESCE(quantity_regular, 0),
        quantity_collection_foil = COALESCE(quantity_foil, 0)
    """)

    # Drop new columns
    logger.info("Dropping new columns")
    with op.batch_alter_table('cards', schema=None) as batch_op:
        batch_op.drop_column('quantity_regular')
        batch_op.drop_column('quantity_foil')

    # Recreate materialized views
    logger.info("Recreating materialized views")
    op.execute("""
    CREATE MATERIALIZED VIEW set_collection_counts AS
    SELECT
        set_code,
        COALESCE(SUM(quantity_collection_regular + quantity_collection_foil), 0) AS collection_count
    FROM cards
    GROUP BY set_code;
    """)
    
    op.execute("CREATE UNIQUE INDEX ON set_collection_counts (set_code);")

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

    logger.info("Downgrade process completed")
