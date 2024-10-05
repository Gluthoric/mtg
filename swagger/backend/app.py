import logging
from flask import Flask, current_app, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from flask.cli import with_appcontext
from flasgger import Swagger
from flask.json import JSONEncoder
from config import config
from database import db
from routes import register_routes
from routes.card_routes import card_routes
from routes.collection_routes import collection_routes
from routes.import_routes import import_routes
from routes.kiosk_routes import kiosk_routes
from routes.set_routes import set_routes
from models.set_collection_count import SetCollectionCount
from errors import handle_error
import redis
import orjson

class ORJSONEncoder(JSONEncoder):
    def default(self, obj):
        return orjson.dumps(obj).decode()

def create_app(config_name='default'):
    # Initialize Flask app
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    app.logger.setLevel(app.config.get('LOG_LEVEL', 'WARNING'))
    logging.getLogger('sqlalchemy.engine').setLevel(app.config.get('SQLALCHEMY_LOG_LEVEL', 'WARNING'))

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)

    # Initialize Swagger
    swagger_config = {
        "swagger": "2.0",
        "info": {
            "title": "MTG Card Manager API",
            "description": "API for managing Magic: The Gathering card collections",
            "version": "1.0.0"
        },
        "host": app.config.get('SWAGGER_HOST', 'localhost:5000'),
        "basePath": "/api",
    }
    Swagger(app, config=swagger_config)

    # Import models here
    from models import Card, Set, SetCollectionCount

    # Initialize Redis
    try:
        app.redis_client = redis.Redis(
            host=app.config['REDIS_HOST'],
            port=app.config['REDIS_PORT'],
            db=app.config['REDIS_DB']
        )
        app.logger.info("Successfully connected to Redis")
    except redis.ConnectionError as e:
        app.logger.error(f"Failed to connect to Redis: {e}")

    # Register routes
    register_routes(app)
    app.register_blueprint(card_routes, url_prefix='/api/cards')
    app.register_blueprint(collection_routes, url_prefix='/api/collections')
    app.register_blueprint(import_routes, url_prefix='/api/imports')
    app.register_blueprint(kiosk_routes, url_prefix='/api/kiosk')
    app.register_blueprint(set_routes, url_prefix='/api/sets')

    # Use ORJSON for JSON serialization
    app.json_encoder = ORJSONEncoder

    # Register error handlers
    register_error_handlers(app)

    # Register the custom CLI command
    @app.cli.command("refresh-collection-counts")
    @with_appcontext
    def refresh_collection_counts():
        """Refresh the set_collection_counts materialized view."""
        app.logger.info("CLI command `refresh-collection-counts` executed.")
        SetCollectionCount.refresh()
        print("Set collection counts refreshed successfully.")

    # Add a route to list all available routes
    @app.route('/routes', methods=['GET'])
    def list_routes():
        if not app.config['DEBUG']:
            return jsonify({"error": "Not found"}), 404
        output = []
        for rule in current_app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods))
            route = f"{rule.endpoint}: {rule.rule} [{methods}]"
            output.append(route)
        return '\n'.join(output), 200, {'Content-Type': 'text/plain; charset=utf-8'}

    return app

def register_error_handlers(app):
    def handle_error_wrapper(status_code, message, error_type):
        response = {
            "status": status_code,
            "error": error_type,
            "message": message
        }
        return jsonify(response), status_code

    app.register_error_handler(400, lambda e: handle_error_wrapper(400, str(e), 'Bad Request'))
    app.register_error_handler(404, lambda e: handle_error_wrapper(404, str(e), 'Resource not found'))
    app.register_error_handler(500, lambda e: handle_error_wrapper(500, str(e), 'Internal server error'))

if __name__ == '__main__':
    app = create_app()
    app.run()
