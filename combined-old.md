# /home/gluth/mtg/backend/utils.py
```
# utils.py
"""
This module contains utility functions used throughout the application.
It provides helpers for type conversion, caching, and serialization.
"""

import time
from functools import wraps
from flask import current_app, request
from decimal import Decimal
import orjson
import logging

logger = logging.getLogger(__name__)

def safe_float(value):
    """Convert value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def convert_decimals(obj):
    """Recursively convert Decimal objects to float in a data structure."""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def cache_response(timeout=300):
    """Decorator to cache the response of a route."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{request.full_path}"
            redis_client = current_app.redis_client

            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return current_app.response_class(
                    response=cached_data,
                    status=200,
                    mimetype='application/json'
                )

            response = func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, response.get_data())
            return response
        return wrapper
    return decorator

def serialize_cards(cards, quantity_type='collection'):
    """Serialize a list of card objects."""
    return [card.to_dict(quantity_type=quantity_type) for card in cards]```

# /home/gluth/mtg/backend/config.py
```
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Redis configuration
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))

    # Debug settings
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    SQLALCHEMY_ECHO = DEBUG

# Use a single configuration for all environments
config = {
    'default': Config
}
```

# /home/gluth/mtg/backend/app.py
```
import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
from routes.cards_routes import cards_bp
from routes.collection_routes import collection_bp
from routes.kiosk_routes import kiosk_bp
from routes.cache_routes import cache_bp
import redis
import orjson
import os
from flask.cli import with_appcontext
from models.set_collection_count import SetCollectionCount
from errors import handle_error

# Import utility functions
# convert_decimals: Converts Decimal objects to float in data structures
# safe_float: Safely converts values to float
# cache_response: Decorator for caching route responses
# serialize_cards: Serializes a list of card objects
from utils import convert_decimals, safe_float, cache_response, serialize_cards

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)

    app.logger.setLevel(logging.WARNING)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)

    # Initialize Redis
    app.redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )

    # Register routes
    register_routes(app)

    # Register blueprints
    app.register_blueprint(set_routes, url_prefix='/api/collection')
    app.register_blueprint(cards_bp)
    app.register_blueprint(collection_bp)
    app.register_blueprint(kiosk_bp)
    app.register_blueprint(cache_bp)

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    # Register error handlers
    app.register_error_handler(400, lambda e: handle_error(400, str(e)))
    app.register_error_handler(404, lambda e: handle_error(404, 'Resource not found'))
    app.register_error_handler(500, lambda e: handle_error(500, 'Internal server error'))

    # Register the custom CLI command
    @app.cli.command("refresh-collection-counts")
    @with_appcontext
    def refresh_collection_counts():
        """Refresh the set_collection_counts materialized view."""
        SetCollectionCount.refresh()
        print("Set collection counts refreshed successfully.")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run()
```

# /home/gluth/mtg/backend/.env
```
DATABASE_URI=postgresql://gluth:Caprisun1!@192.168.1.126:5432/mtg_collection_kiosk
SECRET_KEY=you-will-never-guess
FLASK_APP=main.py
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```

# /home/gluth/mtg/backend/errors.py
```
from flask import jsonify

def handle_error(status_code, message):
    """Create a JSON response for errors."""
    response = jsonify({'error': message})
    response.status_code = status_code
    return response
```

# /home/gluth/mtg/backend/schemas.py
```
from marshmallow import Schema, fields, validate

class UpdateCardSchema(Schema):
    """Schema for updating card quantities."""
    quantity_regular = fields.Integer(required=True, validate=validate.Range(min=0))
    quantity_foil = fields.Integer(required=True, validate=validate.Range(min=0))
```

# /home/gluth/mtg/backend/stats.py
```
from flask import current_app, jsonify
from models.card import Card
from sqlalchemy import func, Float
from database import db
import orjson
import logging

logger = logging.getLogger(__name__)

def get_stats(quantity_regular_field, quantity_foil_field, cache_key):
    """Generic function to get stats for collection or kiosk."""
    redis_client = current_app.redis_client
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(
            func.sum(getattr(Card, quantity_regular_field) + getattr(Card, quantity_foil_field))
        ).scalar() or 0
        unique_cards = Card.query.filter(
            (getattr(Card, quantity_regular_field) > 0) | (getattr(Card, quantity_foil_field) > 0)
        ).count()

        total_value_query = db.session.query(
            func.sum(
                (func.cast(Card.prices['usd'].astext, Float) * getattr(Card, quantity_regular_field)) +
                (func.cast(Card.prices['usd_foil'].astext, Float) * getattr(Card, quantity_foil_field))
            )
        ).filter(
            (getattr(Card, quantity_regular_field) > 0) | (getattr(Card, quantity_foil_field) > 0)
        )
        total_value = total_value_query.scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result).decode()
        redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.exception(f"Error getting stats for {cache_key}: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

# /home/gluth/mtg/backend/models/card.py
```
from database import db
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from sqlalchemy import event
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.set_collection_count import SetCollectionCount

class Card(db.Model):
    __tablename__ = 'cards'

    id = db.Column(db.Text, primary_key=True)
    oracle_id = db.Column(db.Text, index=True)
    multiverse_ids = db.Column(JSONB)
    mtgo_id = db.Column(db.BigInteger)
    arena_id = db.Column(db.BigInteger)
    tcgplayer_id = db.Column(db.BigInteger)
    name = db.Column(db.Text, nullable=False, index=True)
    lang = db.Column(db.Text)
    released_at = db.Column(db.DateTime)
    uri = db.Column(db.Text)
    scryfall_uri = db.Column(db.Text)
    layout = db.Column(db.Text)
    highres_image = db.Column(db.Boolean)
    image_status = db.Column(db.Text)
    image_uris = db.Column(JSONB)
    mana_cost = db.Column(db.Text)
    cmc = db.Column(db.Float)
    type_line = db.Column(db.Text, index=True)
    oracle_text = db.Column(db.Text)
    colors = db.Column(JSONB)
    color_identity = db.Column(JSONB)
    keywords = db.Column(JSONB)
    produced_mana = db.Column(JSONB)
    legalities = db.Column(JSONB)
    games = db.Column(JSONB)
    reserved = db.Column(db.Boolean)
    foil = db.Column(db.Boolean)
    nonfoil = db.Column(db.Boolean)
    finishes = db.Column(JSONB)
    oversized = db.Column(db.Boolean)
    promo = db.Column(db.Boolean)
    full_art = db.Column(db.Boolean)
    textless = db.Column(db.Boolean)
    booster = db.Column(db.Boolean)
    story_spotlight = db.Column(db.Boolean)
    reprint = db.Column(db.Boolean)
    variation = db.Column(db.Boolean)
    set_code = db.Column(db.Text, db.ForeignKey('sets.code'))
    set_name = db.Column(db.Text)
    collector_number = db.Column(db.Text, nullable=False)
    digital = db.Column(db.Boolean)
    rarity = db.Column(db.Text)
    card_back_id = db.Column(db.Text)
    artist = db.Column(db.Text)
    artist_ids = db.Column(JSONB)
    illustration_id = db.Column(db.Text)
    border_color = db.Column(db.Text)
    frame = db.Column(db.Text)
    frame_effects = db.Column(JSONB)
    prices = db.Column(JSONB)
    related_uris = db.Column(JSONB)
    purchase_uris = db.Column(JSONB)
    promo_types = db.Column(JSONB)
    usd_price = db.Column(db.Numeric)
    usd_foil_price = db.Column(db.Numeric)
    quantity_collection_regular = db.Column(db.BigInteger, default=0)
    quantity_collection_foil = db.Column(db.BigInteger, default=0)
    quantity_kiosk_regular = db.Column(db.BigInteger, default=0)
    quantity_kiosk_foil = db.Column(db.BigInteger, default=0)

    # Relationships
    set = db.relationship('Set', back_populates='cards')

    def to_dict(self, quantity_type='collection'):
        """Serialize the card object to a dictionary."""
        data = {
            'id': self.id,
            'name': self.name,
            'set_name': self.set_name,
            'set_code': self.set_code,
            'collector_number': self.collector_number,
            'type_line': self.type_line,
            'rarity': self.rarity,
            'mana_cost': self.mana_cost,
            'cmc': self.cmc,
            'oracle_text': self.oracle_text,
            'colors': self.colors,
            'image_uris': self.image_uris,
            'prices': self.prices,
            'frame_effects': self.frame_effects,
            'promo_types': self.promo_types,
            'promo': self.promo,
            'reprint': self.reprint,
            'variation': self.variation,
            'oversized': self.oversized,
            'keywords': self.keywords,
        }
        if quantity_type == 'collection':
            data['quantity_regular'] = self.quantity_collection_regular
            data['quantity_foil'] = self.quantity_collection_foil
        elif quantity_type == 'kiosk':
            data['quantity_regular'] = self.quantity_kiosk_regular
            data['quantity_foil'] = self.quantity_kiosk_foil
        else:
            data['quantity_regular'] = 0
            data['quantity_foil'] = 0
        return data

@event.listens_for(Session, 'after_flush')
def after_flush(session, flush_context):
    updated_set_codes = set()
    for instance in session.new.union(session.dirty).union(session.deleted):
        if isinstance(instance, Card):
            updated_set_codes.add(instance.set_code)

    if updated_set_codes:
        SetCollectionCount.refresh()
```

# /home/gluth/mtg/backend/routes/card_routes.py
```
import pandas as pd
import logging
from flask import Blueprint, jsonify, request, current_app
import time
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import load_only, joinedload, subqueryload, aliased
from sqlalchemy import func, case, or_, distinct, Float, cast
from sqlalchemy.sql import asc, desc, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.card import Card
from models.set import Set
from models.set_collection_count import SetCollectionCount
from database import db
import orjson
from decimal import Decimal
from collections import defaultdict
from schemas import UpdateCardSchema
from stats import get_stats

card_routes = Blueprint('card_routes', __name__)

def get_category_case():
    return case(
        (Set.set_type.in_(['core', 'expansion']), 'Standard Sets'),
        (Set.set_type.in_(['draft_innovation', 'masters']), 'Special Sets'),
        (Set.set_type == 'funny', 'Un-Sets'),
        (Set.set_type == 'commander', 'Commander Sets'),
        else_='Other'
    )

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def monitor_cache(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Increment total calls
        current_app.redis_client.incr('cache_total_calls')

        # Increment hits or misses
        if result is not None:
            current_app.redis_client.incr('cache_hits')
        else:
            current_app.redis_client.incr('cache_misses')

        # Record response time
        current_app.redis_client.lpush('cache_response_times', end_time - start_time)
        current_app.redis_client.ltrim('cache_response_times', 0, 999)  # Keep last 1000 response times

        return result
    return wrapper

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def serialize_cards(cards, quantity_type='collection'):
    return [card.to_dict() for card in cards]

@card_routes.route('/cards', methods=['GET'])
def get_cards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    name = request.args.get('name', '')
    set_code = request.args.get('set_code', '')
    rarity = request.args.get('rarity', '')
    colors = request.args.get('colors', '').split(',') if request.args.get('colors') else []

    query = Card.query

    if name:
        query = query.filter(Card.name.ilike(f'%{name}%'))
    if set_code:
        query = query.filter(Card.set_code == set_code)
    if rarity:
        query = query.filter(Card.rarity == rarity)
    if colors:
        query = query.filter(or_(*[Card.colors.contains([color.strip()]) for color in colors]))

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200

@card_routes.route('/cards/<string:card_id>', methods=['GET'])
def get_card(card_id):
    # First, check if card is in cache
    cached_card = current_app.redis_client.get(f"card:{card_id}")
    if cached_card:
        return jsonify(orjson.loads(cached_card)), 200

    # Fetch card from database, with optimization to load only the required fields
    card = Card.query.options(
        load_only(
            Card.id,
            Card.name,
            Card.image_uris,
            Card.collector_number,
            Card.prices,
            Card.rarity,
            Card.set_name,
            Card.set_code,
            Card.type_line,
            Card.mana_cost,
            Card.cmc,
            Card.oracle_text,
            Card.colors,
            Card.quantity_collection_regular,
            Card.quantity_collection_foil,
            Card.quantity_kiosk_regular,
            Card.quantity_kiosk_foil,
            Card.frame_effects,
            Card.promo_types,
            Card.promo,
            Card.reprint,
            Card.variation,
            Card.oversized,
            Card.keywords
        )
    ).filter_by(id=card_id).first()

    if not card:
        return jsonify({"error": "Card not found."}), 404

    # Serialize card data
    serialized_card = orjson.dumps(card.to_dict()).decode()

    # Store serialized card in cache for 5 minutes
    current_app.redis_client.setex(f"card:{card_id}", 300, serialized_card)

    return jsonify(card.to_dict()), 200

@card_routes.route('/cards/bulk', methods=['POST'])
def get_bulk_cards():
    data = request.json
    card_ids = data.get('card_ids', [])
    if not card_ids:
        return jsonify({"error": "No card IDs provided."}), 400

    # Check if cards are already in cache
    cards_data = []
    card_ids_to_query = []
    for card_id in card_ids:
        cached_card = current_app.redis_client.get(f"card:{card_id}")
        if cached_card:
            cards_data.append(orjson.loads(cached_card))
        else:
            card_ids_to_query.append(card_id)

    # Fetch cards from database that were not in cache
    if card_ids_to_query:
        cards = Card.query.options(
            load_only(
                Card.id,
                Card.name,
                Card.image_uris,
                Card.collector_number,
                Card.prices,
                Card.rarity,
                Card.set_name,
                Card.set_code,
                Card.type_line,
                Card.mana_cost,
                Card.cmc,
                Card.oracle_text,
                Card.colors,
                Card.quantity_collection_regular,
                Card.quantity_collection_foil,
                Card.quantity_kiosk_regular,
                Card.quantity_kiosk_foil,
                Card.frame_effects,
                Card.promo_types,
                Card.promo,
                Card.reprint,
                Card.variation,
                Card.oversized,
                Card.keywords
            )
        ).filter(Card.id.in_(card_ids_to_query)).all()

        for card in cards:
            serialized_card = orjson.dumps(card.to_dict()).decode()
            # Cache each card for 5 minutes
            current_app.redis_client.setex(f"card:{card.id}", 300, serialized_card)
            cards_data.append(card.to_dict())

    return jsonify({"cards": cards_data}), 200

@card_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
    # Construct cache key
    cache_key = f"set_cards:{set_code}"
    cached_data = current_app.redis_client.get(cache_key)
    if cached_data:
        return jsonify(orjson.loads(cached_data)), 200

    # Fetch all cards for the set, loading only necessary fields
    cards = Card.query.options(
        load_only(
            Card.id,
            Card.name,
            Card.image_uris,
            Card.collector_number,
            Card.prices,
            Card.rarity,
            Card.set_name,
            Card.set_code,
            Card.type_line,
            Card.mana_cost,
            Card.cmc,
            Card.oracle_text,
            Card.colors,
            Card.quantity_collection_regular,
            Card.quantity_collection_foil,
            Card.quantity_kiosk_regular,
            Card.quantity_kiosk_foil,
            Card.frame_effects,
            Card.promo_types,
            Card.promo,
            Card.reprint,
            Card.variation,
            Card.oversized,
            Card.keywords
        )
    ).filter(Card.set_code == set_code).all()

    # Serialize cards data
    cards_data = [card.to_dict() for card in cards]
    serialized_data = orjson.dumps(cards_data).decode()

    # Store serialized set cards in cache for 5 minutes
    current_app.redis_client.setex(cache_key, 300, serialized_data)

    return jsonify({"cards": cards_data}), 200

@card_routes.route('/cards/search', methods=['GET'])
def search_cards():
    query_param = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Card.query.options(load_only(
        Card.id, Card.name, Card.set_name, Card.set_code, Card.collector_number,
        Card.type_line, Card.rarity, Card.mana_cost, Card.cmc, Card.oracle_text,
        Card.colors, Card.image_uris, Card.prices, Card.quantity_collection_regular,
        Card.quantity_collection_foil, Card.quantity_kiosk_regular, Card.quantity_kiosk_foil,
        Card.frame_effects, Card.promo_types, Card.promo, Card.reprint, Card.variation,
        Card.oversized, Card.keywords
    )).filter(
        or_(
            Card.name.ilike(f'%{query_param}%'),
            Card.type_line.ilike(f'%{query_param}%'),
            Card.oracle_text.ilike(f'%{query_param}%')
        )
    )

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200

# Collection Routes

@card_routes.route('/collection', methods=['GET'])
def get_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    set_code = request.args.get('set_code', '', type=str)

    cache_key = f"collection:page:{page}:per_page:{per_page}:set_code:{set_code}"

    @monitor_cache
    def get_cached_data(key):
        return current_app.redis_client.get(key)

    cached_data = get_cached_data(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    query = Card.query

    if set_code:
        query = query.filter(Card.set_code == set_code)

    query = query.filter((Card.quantity_regular > 0) | (Card.quantity_foil > 0))

    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'collection': serialize_cards(collection.items, quantity_type='collection'),
        'total': collection.total,
        'pages': collection.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result).decode()

    # Dynamically set cache expiration based on data size
    cache_expiration = min(300, max(60, len(serialized_data) // 1000))  # Between 1-5 minutes based on size
    current_app.redis_client.setex(cache_key, cache_expiration, serialized_data)

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/collection/sets', methods=['GET'])
def get_collection_sets():
    try:
        # Extract query parameters
        name = request.args.get('name', type=str)
        set_types = request.args.getlist('set_type[]')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        # Log received parameters
        logger.info(f"get_collection_sets: Received parameters: name={name}, set_types={set_types}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Construct cache key
        cache_key = f"collection_sets:name:{name}:set_type:{','.join(set_types)}:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
        cached_data = current_app.redis_client.get(cache_key)

        if cached_data:
            logger.info("get_collection_sets: Returning cached data")
            return current_app.response_class(
                response=cached_data.decode(),
                status=200,
                mimetype='application/json'
            )

        logger.info("get_collection_sets: Cache miss, fetching data from database")

        # Define valid sort fields and prevent SQL injection
        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(f"get_collection_sets: {error_message}")
            return jsonify({"error": error_message}), 400

        # Determine sort column
        if sort_by == 'collection_count':
            sort_column = SetCollectionCount.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        # Apply sort order
        order_func = desc if sort_order.lower() == 'desc' else asc

        # Subquery for total value
        value_subquery = (
            db.session.query(
                Card.set_code,
                func.sum(
                    (func.cast(Card.prices['usd'].astext, Float) * Card.quantity_regular) +
                    (func.cast(Card.prices['usd_foil'].astext, Float) * Card.quantity_foil)
                ).label('total_value')
            )
            .group_by(Card.set_code)
            .subquery()
        )

        # Main query
        query = (
            db.session.query(
                Set,
                func.coalesce(SetCollectionCount.collection_count, 0).label('collection_count'),
                func.coalesce(value_subquery.c.total_value, 0).label('total_value')
            )
            .join(SetCollectionCount, Set.code == SetCollectionCount.set_code)
            .outerjoin(value_subquery, Set.code == value_subquery.c.set_code)
        )

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.debug(f"get_collection_sets: Applied filter: Set.name ilike '%{name}%'")
        if set_types:
            query = query.filter(Set.set_type.in_(set_types))
            logger.debug(f"get_collection_sets: Applied filter: Set.set_type IN {set_types}")
        else:
            default_set_types = ['core', 'expansion', 'masters', 'draft_innovation', 'funny', 'commander']
            query = query.filter(Set.set_type.in_(default_set_types))
            logger.debug("get_collection_sets: Applied filter: Using partial index for relevant set types")

        # Apply sorting
        query = query.order_by(order_func(sort_column))

        # Execute the query with pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"get_collection_sets: Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

        # Process results
        sets_list = []
        for set_instance, collection_count, total_value in paginated_sets.items:
            set_data = set_instance.to_dict()
            set_data['collection_count'] = collection_count
            set_data['collection_percentage'] = (collection_count / set_instance.card_count) * 100 if set_instance.card_count else 0
            set_data['total_value'] = round(total_value, 2)
            sets_list.append(set_data)

        # Build response
        response = {
            'sets': sets_list,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any Decimal objects to float
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

        logger.info(f"Returning response with {len(sets_list)} sets")
        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred in get_collection_sets: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

@card_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    schema = UpdateCardSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify({"error": errors}), 400

    data = schema.load(request.json)
    quantity_regular = data['quantity_regular']
    quantity_foil = data['quantity_foil']

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    old_set_code = card.set_code
    card.quantity_collection_regular = quantity_regular
    card.quantity_collection_foil = quantity_foil

    db.session.commit()

    # Invalidate specific caches
    current_app.redis_client.delete(f"collection:set:{old_set_code}")
    current_app.redis_client.delete(f"collection_sets:{old_set_code}")
    current_app.redis_client.delete("collection_stats")

    card_data = card.to_dict()

    return current_app.response_class(
        response=orjson.dumps(card_data).decode(),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/collection/stats', methods=['GET'])
def get_collection_stats():
    return get_stats('quantity_collection_regular', 'quantity_collection_foil', 'collection_stats')

@card_routes.route('/collection/sets/<string:set_code>/cards', methods=['GET'])
def get_collection_set_cards(set_code):
    name = request.args.get('name', '', type=str)
    rarities = request.args.getlist('rarities') + request.args.getlist('rarities[]')
    colors = request.args.getlist('colors') + request.args.getlist('colors[]')
    types = request.args.getlist('types') + request.args.getlist('types[]')
    keyword = request.args.get('keyword', '', type=str)

    try:
        # Build the query with only required columns using model attributes
        query = Card.query.options(
            load_only(
                Card.id,
                Card.name,
                Card.image_uris,
                Card.collector_number,
                Card.prices,
                Card.rarity,
                Card.set_name,
                Card.quantity_collection_regular,
                Card.quantity_collection_foil,
                Card.type_line,
                Card.colors,
                Card.keywords
            )
        ).filter(Card.set_code == set_code)

        # Apply filters
        if name:
            query = query.filter(Card.name.ilike(f'%{name}%'))
        if rarities:
            query = query.filter(Card.rarity.in_(rarities))
        if colors:
            VALID_COLORS = {'W', 'U', 'B', 'R', 'G', 'C'}
            invalid_colors = set(colors) - VALID_COLORS
            if invalid_colors:
                return jsonify({"error": f"Invalid colors: {', '.join(invalid_colors)}"}), 400

            # Handle "C" for colorless cards
            if 'C' in colors:
                colors.remove('C')
                # Filter for colorless cards where the 'colors' array is empty
                colorless_filter = func.jsonb_array_length(Card.colors) == 0
            else:
                colorless_filter = None

            # Build the colors filter for colored cards
            if colors:
                colors_filter = Card.colors.overlap(colors)
                if colorless_filter is not None:
                    final_colors_filter = or_(colors_filter, colorless_filter)
                else:
                    final_colors_filter = colors_filter
            else:
                # Only colorless cards are selected
                final_colors_filter = colorless_filter

            # Apply the final colors filter
            if final_colors_filter is not None:
                query = query.filter(final_colors_filter)
        if types:
            type_filters = [Card.type_line.ilike(f'%{type_}%') for type_ in types]
            query = query.filter(or_(*type_filters))
        if keyword:
            query = query.filter(Card.keywords.contains([keyword]))

        # Sort by collector number as integer
        query = query.order_by(func.cast(func.regexp_replace(Card.collector_number, '[^0-9]', '', 'g'), db.Integer))

        # Execute the query
        cards = query.all()

        # Prepare the response
        result = {
            'cards': [{
                'id': card.id,
                'name': card.name,
                'image_uris': card.image_uris,
                'collector_number': card.collector_number,
                'prices': card.prices,
                'rarity': card.rarity,
                'set_name': card.set_name,
                'quantity_regular': card.quantity_collection_regular,
                'quantity_foil': card.quantity_collection_foil,
                'type_line': card.type_line,
                'colors': card.colors,
                'keywords': card.keywords
            } for card in cards],
            'total': len(cards),
        }

        return jsonify(result), 200
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

# Kiosk Routes

@card_routes.route('/kiosk', methods=['GET'])
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cache_key = f"kiosk:page:{page}:per_page:{per_page}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    kiosk = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'kiosk': serialize_cards(kiosk.items, quantity_type='kiosk'),
        'total': kiosk.total,
        'pages': kiosk.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result).decode()
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/sets', methods=['GET'])
def get_kiosk_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sortBy', 'released_at')
    sort_order = request.args.get('sortOrder', 'desc')

    cache_key = f"kiosk_sets:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    try:
        kiosk_sets = db.session.query(Set).\
            join(Card, Card.set_code == Set.code).\
            filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
            distinct()

        if sort_by == 'released_at':
            if sort_order == 'desc':
                kiosk_sets = kiosk_sets.order_by(Set.released_at.desc())
            else:
                kiosk_sets = kiosk_sets.order_by(Set.released_at)
        else:
            if sort_order == 'desc':
                kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by).desc())
            else:
                kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by))

        paginated_sets = kiosk_sets.paginate(page=page, per_page=per_page, error_out=False)

        sets_data = []
        for set_obj in paginated_sets.items:
            set_dict = set_obj.to_dict()

            kiosk_count = db.session.query(func.count(distinct(Card.id))).\
                filter(Card.set_code == set_obj.code).\
                filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
                scalar()

            kiosk_percentage = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

            # Calculate total_value for the set
            total_value_query = db.session.query(
                func.sum(
                    (func.cast((Card.prices['usd'].astext).cast(Float), Float) * Card.quantity_kiosk_regular) +
                    (func.cast((Card.prices['usd_foil'].astext).cast(Float), Float) * Card.quantity_kiosk_foil)
                )
            ).filter(Card.set_code == set_obj.code)

            total_value = total_value_query.scalar() or 0.0

            set_dict['kiosk_count'] = kiosk_count
            set_dict['kiosk_percentage'] = kiosk_percentage
            set_dict['total_value'] = round(total_value, 2)

            sets_data.append(set_dict)

        # Convert Decimal objects to float
        sets_data = convert_decimals(sets_data)

        response = {
            'sets': sets_data,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any remaining Decimal objects in the response
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 600, serialized_data)  # Cache for 10 minutes

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

@card_routes.route('/kiosk/sets/<string:set_code>/cards', methods=['GET'])
def get_kiosk_set_cards(set_code):
    name_filter = request.args.get('name', '')
    rarity_filter = request.args.get('rarity', '')
    sort_by = request.args.get('sortBy', 'name')
    sort_order = request.args.get('sortOrder', 'asc')

    cache_key = f"kiosk_set_cards:{set_code}:name:{name_filter}:rarity:{rarity_filter}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    query = Card.query.filter(Card.set_code == set_code).filter(
        (Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)
    )

    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))
    if rarity_filter:
        query = query.filter(Card.rarity == rarity_filter)

    if sort_order == 'desc':
        query = query.order_by(getattr(Card, sort_by).desc())
    else:
        query = query.order_by(getattr(Card, sort_by))

    cards = query.all()
    cards_data = serialize_cards(cards, quantity_type='kiosk')

    set_instance = Set.query.filter_by(code=set_code).first()
    set_name = set_instance.name if set_instance else ''

    result = {
        'cards': cards_data,
        'set_name': set_name
    }

    serialized_data = orjson.dumps(result).decode()
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/<string:card_id>', methods=['POST', 'PUT'])
def update_kiosk(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    card.quantity_kiosk_regular = quantity_regular
    card.quantity_kiosk_foil = quantity_foil

    db.session.commit()

    # Invalidate related caches
    current_app.redis_client.delete("kiosk:*")
    current_app.redis_client.delete("kiosk_sets:*")
    current_app.redis_client.delete(f"kiosk_set_cards:{card.set_code}:*")

    # Serialize and return updated card
    card_data = card.to_dict()
    card_data.update({
        'quantity_regular': card.quantity_kiosk_regular,
        'quantity_foil': card.quantity_kiosk_foil
    })

    return current_app.response_class(
        response=orjson.dumps(card_data).decode(),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/stats', methods=['GET'])
def get_kiosk_stats():
    cache_key = "kiosk_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(func.sum(Card.quantity_kiosk_regular + Card.quantity_kiosk_foil)).scalar() or 0
        unique_cards = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).count()

        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_kiosk_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_kiosk_foil)
            )
            FROM cards
            WHERE quantity_kiosk_regular > 0 OR quantity_kiosk_foil > 0
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result).decode()
        current_app.redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@card_routes.route('/cache_stats', methods=['GET'])
def get_cache_stats():
    total_calls = int(current_app.redis_client.get('cache_total_calls') or 0)
    hits = int(current_app.redis_client.get('cache_hits') or 0)
    misses = int(current_app.redis_client.get('cache_misses') or 0)

    hit_rate = (hits / total_calls * 100) if total_calls > 0 else 0

    response_times = current_app.redis_client.lrange('cache_response_times', 0, -1)
    avg_response_time = sum(float(t) for t in response_times) / len(response_times) if response_times else 0

    return jsonify({
        'total_calls': total_calls,
        'hits': hits,
        'misses': misses,
        'hit_rate': f"{hit_rate:.2f}%",
        'avg_response_time': f"{avg_response_time:.4f} seconds"
    })

@card_routes.route('/collection/sets/<string:set_code>', methods=['GET'])
def get_collection_set(set_code):
    try:
        # Fetch the set instance
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return jsonify({"error": "Set not found."}), 404

        # Serialize set data
        set_data = set_instance.to_dict()

        # Fetch cards for this set
        cards = Card.query.filter_by(set_code=set_code).all()
        set_data['cards'] = [card.to_dict() for card in cards]

        # Calculate statistics
        statistics = {
            'frame_effects': {},
            'promo_types': {},
            'other_attributes': {
                'promo': 0,
                'reprint': 0,
                'variation': 0,
                'oversized': 0
            }
        }

        collection_count = 0
        total_value = 0.0

        for card in cards:
            collection_count += card.quantity_regular + card.quantity_foil

            # Calculate card value
            regular_value = float(card.prices.get('usd', 0) or 0) * card.quantity_regular
            foil_value = float(card.prices.get('usd_foil', 0) or 0) * card.quantity_foil
            total_value += regular_value + foil_value

            if card.frame_effects:
                for effect in card.frame_effects:
                    statistics['frame_effects'][effect] = statistics['frame_effects'].get(effect, 0) + 1
            if card.promo_types:
                for promo_type in card.promo_types:
                    statistics['promo_types'][promo_type] = statistics['promo_types'].get(promo_type, 0) + 1
            if card.promo:
                statistics['other_attributes']['promo'] += 1
            if card.reprint:
                statistics['other_attributes']['reprint'] += 1
            if card.variation:
                statistics['other_attributes']['variation'] += 1
            if card.oversized:
                statistics['other_attributes']['oversized'] += 1

        set_data['collection_count'] = collection_count
        set_data['collection_percentage'] = (collection_count / set_instance.card_count) * 100 if set_instance.card_count else 0
        set_data['total_value'] = round(total_value, 2)
        set_data['statistics'] = statistics

        return jsonify({
            "set": set_data,
            "cards": set_data['cards']
        }), 200
    except Exception as e:
        error_message = f"An error occurred while fetching the set: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500
```