import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
import redis
import orjson
import os
from decimal import Decimal
from flask.cli import with_appcontext
from models.set_collection_count import SetCollectionCount

logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def convert_decimal_to_float(data):
    if isinstance(data, dict):
        return {k: convert_decimal_to_float(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_decimal_to_float(i) for i in data]
    elif isinstance(data, Decimal):
        return float(data)
    return data

def create_app(config_name='default'):
    # Check if we are in development or production mode
    is_production = config_name == 'production'

    # Initialize Flask app
    if is_production:
        app = Flask(__name__, static_folder=os.path.abspath('/home/gluth/mtg/frontend/dist'), static_url_path='')
    else:
        app = Flask(__name__)

    app.logger.setLevel(logging.WARNING)
    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_ECHO'] = app.config['DEBUG']

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)

    # Register routes
    register_routes(app)
    
    # Register set_routes blueprint with the correct URL prefix
    app.register_blueprint(set_routes, url_prefix='/api/collection')

    # Add Redis client to app context
    app.redis_client = redis_client

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

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
