from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
from routes.kiosk_routes import kiosk_routes
import redis
import orjson

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register routes
    register_routes(app)
    app.register_blueprint(set_routes, url_prefix='/api')
    app.register_blueprint(kiosk_routes, url_prefix='/api')

    # Add Redis client to app context
    app.redis_client = redis_client

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)