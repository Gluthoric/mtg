import os
import json
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
from tqdm import tqdm

# Load environment variables from .env
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')

# Scryfall bulk data file and set code
SCRYFALL_BULK_JSON = os.getenv('SCRYFALL_BULK_JSON', 'default_cards.json')
SET_CODE = os.getenv('SET_CODE', 'ALL')

# Define the batch size for bulk inserts
BATCH_SIZE = 1000

def connect_db():
    """Establishes a connection to the PostgreSQL database."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            sslmode='require'  # Ensure SSL connection
        )
        conn.autocommit = False  # Handle transactions manually
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        exit(1)

def load_json(file_path):
    """Loads JSON data from the specified file path."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading JSON file: {e}")
        exit(1)

def prepare_card_record(card):
    """
    Extracts and serializes necessary fields from the Scryfall card data.
    """
    # Serialize JSONB fields
    multiverse_ids = json.dumps(card.get('multiverse_ids', []))
    image_uris = json.dumps(card.get('image_uris', {}))
    colors = json.dumps(card.get('colors', []))
    color_identity = json.dumps(card.get('color_identity', []))
    keywords = json.dumps(card.get('keywords', []))
    produced_mana = json.dumps(card.get('produced_mana', []))
    legalities = json.dumps(card.get('legalities', {}))
    games = json.dumps(card.get('games', []))
    finishes = json.dumps(card.get('finishes', []))
    artist_ids = json.dumps(card.get('artist_ids', []))
    prices = json.dumps(card.get('prices', {}))
    related_uris = json.dumps(card.get('related_uris', {}))
    purchase_uris = json.dumps(card.get('purchase_uris', {}))
    frame_effects = json.dumps(card.get('frame_effects', [])) if 'frame_effects' in card else None
    promo_types = json.dumps(card.get('promo_types', [])) if 'promo_types' in card else None

    return (
        card.get('id'),
        card.get('oracle_id'),
        multiverse_ids,
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
        image_uris,
        card.get('mana_cost'),
        card.get('cmc'),
        card.get('type_line'),
        card.get('oracle_text'),
        colors,
        color_identity,
        keywords,
        produced_mana,
        legalities,
        games,
        card.get('reserved'),
        card.get('foil'),
        card.get('nonfoil'),
        finishes,
        card.get('oversized'),
        card.get('promo'),
        card.get('full_art'),
        card.get('textless'),
        card.get('booster'),
        card.get('story_spotlight'),
        card.get('reprint'),
        card.get('variation'),
        card.get('set'),
        card.get('set_id'),
        card.get('set_name'),
        card.get('collector_number'),
        card.get('digital'),
        card.get('rarity'),
        card.get('card_back_id'),
        card.get('artist'),
        artist_ids,
        card.get('illustration_id'),
        card.get('border_color'),
        card.get('frame'),
        prices,
        related_uris,
        purchase_uris,
        frame_effects,
        promo_types
    )

def upsert_cards(conn, cards):
    """
    Performs an UPSERT (insert or update) operation on the `cards` table.
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
            set_id,
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
            frame_effects,
            promo_types
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
            set_id = EXCLUDED.set_id,
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
            frame_effects = EXCLUDED.frame_effects,
            promo_types = EXCLUDED.promo_types
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

def main():
    """Main function to execute the import process."""
    # Connect to the database
    conn = connect_db()

    # Load the Scryfall bulk data
    print("Loading Scryfall bulk data...")
    data = load_json(SCRYFALL_BULK_JSON)
    print(f"Total cards in bulk data: {len(data)}")

    # Filter cards if SET_CODE is specified
    if SET_CODE and SET_CODE.upper() != 'ALL':
        cards_to_import = [card for card in data if card.get('set') == SET_CODE.lower()]
        print(f"Total cards to import from set '{SET_CODE}': {len(cards_to_import)}")
    else:
        cards_to_import = data
        print(f"Total cards to import (all sets): {len(cards_to_import)}")

    # Prepare card records in batches
    batch = []
    for card in tqdm(cards_to_import, desc="Preparing cards for import"):
        record = prepare_card_record(card)
        batch.append(record)

        # Insert in batches
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
