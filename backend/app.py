import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from flask.cli import with_appcontext
from config import config
from database import db
from routes import register_routes
from routes.card_routes import card_routes
from models.set_collection_count import SetCollectionCount
from errors import handle_error
import redis
import orjson

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)

    # Import models here
    from models import Card, Set, SetCollectionCount

    # Initialize Redis
    app.redis_client = redis.Redis(
        host=app.config['REDIS_HOST'],
        port=app.config['REDIS_PORT'],
        db=app.config['REDIS_DB']
    )

    # Register routes
    register_routes(app)
    app.register_blueprint(card_routes, url_prefix='/api')
    from routes.set_routes import set_routes
    app.register_blueprint(set_routes, url_prefix='/api/sets')

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    # Register error handlers
    register_error_handlers(app)

    # Register the custom CLI command
    @app.cli.command("refresh-collection-counts")
    @with_appcontext
    def refresh_collection_counts():
        """Refresh the set_collection_counts materialized view."""
        SetCollectionCount.refresh()
        print("Set collection counts refreshed successfully.")

    return app

def register_error_handlers(app):
    app.register_error_handler(400, lambda e: handle_error(400, str(e), 'Bad Request'))
    app.register_error_handler(404, lambda e: handle_error(404, str(e), 'Resource not found'))
    app.register_error_handler(500, lambda e: handle_error(500, str(e), 'Internal server error'))

if __name__ == '__main__':
    app = create_app()
    app.run()
