import psycopg2
import json
from psycopg2.extras import execute_values
from tqdm import tqdm
import os

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
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        exit(1)

def prepare_card_record(card):
    """
    Extract necessary fields from the Scryfall card data.
    Modify this function based on your `cards` table schema.
    """
    return (
        card.get('id'),  # Scryfall ID
        card.get('oracle_id'),
        json.dumps(card.get('multiverse_ids', [])),  # Assuming text field storing JSON array
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
        json.dumps(card.get('image_uris', {})),
        card.get('mana_cost'),
        card.get('cmc'),
        card.get('type_line'),
        card.get('oracle_text'),
        json.dumps(card.get('colors', [])),
        json.dumps(card.get('color_identity', [])),
        json.dumps(card.get('keywords', [])),
        json.dumps(card.get('produced_mana', [])),
        json.dumps(card.get('legalities', {})),
        json.dumps(card.get('games', [])),
        card.get('reserved'),
        card.get('foil'),
        card.get('nonfoil'),
        json.dumps(card.get('finishes', [])),
        card.get('oversized'),
        card.get('promo'),
        card.get('reprint'),
        card.get('variation'),
        card.get('set_code'),
        card.get('set_name'),
        card.get('collector_number'),
        card.get('digital'),
        card.get('rarity'),
        card.get('card_back_id'),
        card.get('artist'),
        json.dumps(card.get('artist_ids', [])),
        card.get('illustration_id'),
        card.get('border_color'),
        card.get('frame'),
        card.get('full_art'),
        card.get('textless'),
        card.get('booster'),
        json.dumps(card.get('prices', {})),
        json.dumps(card.get('related_uris', {})),
        json.dumps(card.get('purchase_uris', {}))
    )

def upsert_cards(conn, cards):
    """
    Perform upsert (insert or update) on the `cards` table using execute_values.
    """
    with conn.cursor() as cur:
        # Define the SQL query for upsert using execute_values
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
            full_art,
            textless,
            booster,
            prices,
            related_uris,
            purchase_uris
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
            full_art = EXCLUDED.full_art,
            textless = EXCLUDED.textless,
            booster = EXCLUDED.booster,
            prices = EXCLUDED.prices,
            related_uris = EXCLUDED.related_uris,
            purchase_uris = EXCLUDED.purchase_uris;
        """

        # Use execute_values for efficient bulk upsert
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

def main():
    # Connect to the database
    conn = connect_db()

    # Load the Scryfall bulk data
    data = load_json(SCRYFALL_BULK_JSON)
    print(f"Total cards to process: {len(data)}")

    # Process and upsert cards in batches
    batch = []
    for card in tqdm(data, desc="Processing cards"):
        batch.append(prepare_card_record(card))
        if len(batch) >= BATCH_SIZE:
            upsert_cards(conn, batch)
            batch = []

    # Insert any remaining cards
    if batch:
        upsert_cards(conn, batch)

    # Close the database connection
    conn.close()
    print("Import completed successfully.")

if __name__ == "__main__":
    main()
