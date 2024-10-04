import logging
from flask import Flask
from routes import register_routes

def create_app(config_name='default'):
    app = Flask(__name__)
    # ... (other configurations)
    
    register_routes(app)
    
    # ... (rest of the setup)
    return app
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from database import db
from routes.set_routes import set_routes
from routes.cards_routes import cards_bp
from routes.collection_routes import collection_bp
from routes.kiosk_routes import kiosk_bp
from routes.cache_routes import cache_bp
import redis
import orjson
from flask.cli import with_appcontext
from models.set_collection_count import SetCollectionCount
from errors import handle_error

# Import utility functions
from utils import convert_decimals, safe_float, cache_response, serialize_cards

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

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
