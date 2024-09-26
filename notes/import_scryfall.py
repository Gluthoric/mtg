import psycopg2
from psycopg2.extras import execute_values
import json
from tqdm import tqdm

# Database connection parameters
DB_HOST = 'aws-0-us-west-1.pooler.supabase.com'
DB_PORT = '6543'
DB_NAME = 'postgres'
DB_USER = 'postgres.xbuiunafhcscvjftnvxr'
DB_PASSWORD = 'Timothy2-Sample-Underwent'  # Replace with your actual password

# Path to the Scryfall bulk data JSON file
SCRYFALL_BULK_JSON = 'scryfall_default_cards.json'  # Ensure this path is correct

# Define the batch size for inserts
BATCH_SIZE = 1000

def connect_db():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        conn.autocommit = False  # Manage transactions manually
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

def load_json(file_path):
    """Loads the JSON data from the specified file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        exit(1)

def prepare_card_record(card):
    """
    Extracts necessary fields from the Scryfall card data.
    Adjust this function based on your `cards` table schema.
    """
    return (
        card.get('id'),  # Scryfall ID (primary key)
        card.get('oracle_id'),
        card.get('multiverse_ids', []),  # JSONB field
        card.get('mtgo_id'),
        card.get('arena_id'),
        card.get('tcgplayer_id'),
        card.get('name'),
        card.get('lang'),
        card.get('released_at'),
        card.get('uri'),
        card.get('scryfall_uri'),
        card.get('layout'),
        card.get('highres_image'),
        card.get('image_status'),
        card.get('image_uris', {}),  # JSONB field
        card.get('mana_cost'),
        card.get('cmc'),
        card.get('type_line'),
        card.get('oracle_text'),
        card.get('colors', []),  # JSONB field
        card.get('color_identity', []),  # JSONB field
        card.get('keywords', []),  # JSONB field
        card.get('produced_mana', []),  # JSONB field
        card.get('legalities', {}),  # JSONB field
        card.get('games', []),  # JSONB field
        card.get('reserved'),
        card.get('foil'),
        card.get('nonfoil'),
        card.get('finishes', []),  # JSONB field
        card.get('oversized'),
        card.get('promo'),
        card.get('full_art'),
        card.get('textless'),
        card.get('booster'),
        card.get('story_spotlight'),
        card.get('reprint'),
        card.get('variation'),
        card.get('set'),  # set_code
        card.get('set_name'),
        card.get('collector_number'),
        card.get('digital'),
        card.get('rarity'),
        card.get('card_back_id'),
        card.get('artist'),
        card.get('artist_ids', []),  # JSONB field
        card.get('illustration_id'),
        card.get('border_color'),
        card.get('frame'),
        card.get('prices', {}),  # JSONB field
        card.get('related_uris', {}),  # JSONB field
        card.get('purchase_uris', {}),  # JSONB field
        card.get('variation_of'),
        card.get('security_stamp'),
        card.get('watermark'),
    )

def upsert_cards(conn, cards):
    """
    Performs upsert (insert or update) on the `cards` table using execute_values.
    """
    with conn.cursor() as cur:
        sql = """
        INSERT INTO public.cards (
            id,
            oracle_id,
            multiverse_ids,
            mtgo_id,
            arena_id,
            tcgplayer_id,
            name,
            lang,
            released_at,
            uri,
            scryfall_uri,
            layout,
            highres_image,
            image_status,
            image_uris,
            mana_cost,
            cmc,
            type_line,
            oracle_text,
            colors,
            color_identity,
            keywords,
            produced_mana,
            legalities,
            games,
            reserved,
            foil,
            nonfoil,
            finishes,
            oversized,
            promo,
            full_art,
            textless,
            booster,
            story_spotlight,
            reprint,
            variation,
            set_code,
            set_name,
            collector_number,
            digital,
            rarity,
            card_back_id,
            artist,
            artist_ids,
            illustration_id,
            border_color,
            frame,
            prices,
            related_uris,
            purchase_uris,
            variation_of,
            security_stamp,
            watermark
        ) VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            oracle_id = EXCLUDED.oracle_id,
            multiverse_ids = EXCLUDED.multiverse_ids,
            mtgo_id = EXCLUDED.mtgo_id,
            arena_id = EXCLUDED.arena_id,
            tcgplayer_id = EXCLUDED.tcgplayer_id,
            name = EXCLUDED.name,
            lang = EXCLUDED.lang,
            released_at = EXCLUDED.released_at,
            uri = EXCLUDED.uri,
            scryfall_uri = EXCLUDED.scryfall_uri,
            layout = EXCLUDED.layout,
            highres_image = EXCLUDED.highres_image,
            image_status = EXCLUDED.image_status,
            image_uris = EXCLUDED.image_uris,
            mana_cost = EXCLUDED.mana_cost,
            cmc = EXCLUDED.cmc,
            type_line = EXCLUDED.type_line,
            oracle_text = EXCLUDED.oracle_text,
            colors = EXCLUDED.colors,
            color_identity = EXCLUDED.color_identity,
            keywords = EXCLUDED.keywords,
            produced_mana = EXCLUDED.produced_mana,
            legalities = EXCLUDED.legalities,
            games = EXCLUDED.games,
            reserved = EXCLUDED.reserved,
            foil = EXCLUDED.foil,
            nonfoil = EXCLUDED.nonfoil,
            finishes = EXCLUDED.finishes,
            oversized = EXCLUDED.oversized,
            promo = EXCLUDED.promo,
            full_art = EXCLUDED.full_art,
            textless = EXCLUDED.textless,
            booster = EXCLUDED.booster,
            story_spotlight = EXCLUDED.story_spotlight,
            reprint = EXCLUDED.reprint,
            variation = EXCLUDED.variation,
            set_code = EXCLUDED.set_code,
            set_name = EXCLUDED.set_name,
            collector_number = EXCLUDED.collector_number,
            digital = EXCLUDED.digital,
            rarity = EXCLUDED.rarity,
            card_back_id = EXCLUDED.card_back_id,
            artist = EXCLUDED.artist,
            artist_ids = EXCLUDED.artist_ids,
            illustration_id = EXCLUDED.illustration_id,
            border_color = EXCLUDED.border_color,
            frame = EXCLUDED.frame,
            prices = EXCLUDED.prices,
            related_uris = EXCLUDED.related_uris,
            purchase_uris = EXCLUDED.purchase_uris,
            variation_of = EXCLUDED.variation_of,
            security_stamp = EXCLUDED.security_stamp,
            watermark = EXCLUDED.watermark
        ;
        """
        try:
            execute_values(
                cur, sql, cards,
                template=None,
                page_size=BATCH_SIZE
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error during upsert: {e}")

def prepare_set_record(card):
    """
    Extracts set information from the card data.
    """
    return (
        card.get('set'),        # code
        card.get('set_id'),
        card.get('set_name'),
        card.get('released_at'),
        card.get('set_type'),
        0,  # card_count will be updated later
        card.get('digital'),
        card.get('foil_only'),
        card.get('icon_svg_uri')
    )

def upsert_sets(conn, sets_data):
    """
    Performs upsert on the `sets` table.
    """
    with conn.cursor() as cur:
        sql = """
        INSERT INTO public.sets (
            code,
            id,
            name,
            released_at,
            set_type,
            card_count,
            digital,
            foil_only,
            icon_svg_uri
        ) VALUES %s
        ON CONFLICT (code) DO UPDATE SET
            id = EXCLUDED.id,
            name = EXCLUDED.name,
            released_at = EXCLUDED.released_at,
            set_type = EXCLUDED.set_type,
            digital = EXCLUDED.digital,
            foil_only = EXCLUDED.foil_only,
            icon_svg_uri = EXCLUDED.icon_svg_uri
        ;
        """
        try:
            execute_values(
                cur, sql, sets_data,
                template=None,
                page_size=BATCH_SIZE
            )
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error during sets upsert: {e}")

def update_set_card_counts(conn):
    """
    Updates the card_count field in the sets table to reflect the number of non-variant cards.
    """
    with conn.cursor() as cur:
        sql = """
        UPDATE public.sets s SET card_count = sub.count
        FROM (
            SELECT set_code, COUNT(*) AS count
            FROM public.cards
            WHERE (variation = FALSE OR variation IS NULL)
            GROUP BY set_code
        ) AS sub
        WHERE s.code = sub.set_code;
        """
        try:
            cur.execute(sql)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Error updating set card counts: {e}")

def main():
    """Main function to execute the import process."""
    # Connect to the database
    conn = connect_db()

    # Load the Scryfall bulk data
    data = load_json(SCRYFALL_BULK_JSON)
    print(f"Total cards to process: {len(data)}")

    # Collect set data
    sets_seen = {}
    sets_data = []

    # Process and upsert cards in batches
    batch = []
    for card in tqdm(data, desc="Processing cards", total=len(data)):
        # Prepare card record
        batch.append(prepare_card_record(card))

        # Collect set information
        set_code = card.get('set')
        if set_code not in sets_seen:
            sets_seen[set_code] = prepare_set_record(card)
            sets_data.append(sets_seen[set_code])

        if len(batch) >= BATCH_SIZE:
            upsert_cards(conn, batch)
            batch = []

    # Insert any remaining cards
    if batch:
        upsert_cards(conn, batch)

    # Upsert sets
    upsert_sets(conn, sets_data)

    # Update card counts in sets
    update_set_card_counts(conn)

    # Close the database connection
    conn.close()
    print("Import completed successfully.")

if __name__ == "__main__":
    main()
