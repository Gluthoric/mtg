from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from database import db
from routes import register_routes
import redis
import orjson
import os

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_app(config_name='default'):
    # Check if we are in development or production mode
    is_production = config_name == 'production'

    # Only serve static files in production
    if is_production:
        app = Flask(__name__, static_folder=os.path.abspath('/home/gluth/mtg/frontend/dist'), static_url_path='')
    else:
        app = Flask(__name__)

    app.config.from_object(config[config_name])
    app.config['SQLALCHEMY_ECHO'] = app.config['DEBUG']

    # Initialize extensions
    db.init_app(app)
    CORS(app)
    migrate = Migrate(app, db)

    with app.app_context():
        # Initialize the database
        db.create_all()

    # Register routes
    register_routes(app)

    # Add Redis client to app context
    app.redis_client = redis_client

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    return app

if __name__ == '__main__':
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    app.run(debug=app.config['DEBUG'], host='0.0.0.0', port=5000)
