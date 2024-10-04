Changes Made Thus Far

``` # app.py
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

def handle_error(error_code, error_message):
    return {'error': error_message}, error_code

if __name__ == '__main__':
    app = create_app()
    app.run()
```
``` # config.py

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
``` # utils.py
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
    return [card.to_dict(quantity_type=quantity_type) for card in cards]
```
``` # .env
DATABASE_URI=postgresql://gluth:Caprisun1!@192.168.1.126:5432/mtg_collection_kiosk
SECRET_KEY=you-will-never-guess
FLASK_APP=main.py
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
```