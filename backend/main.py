import logging
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import config
from database import db
from routes import register_routes
import redis
import orjson
import os
from models.set import Set
from decimal import Decimal

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
    app = Flask(__name__)
    app.logger.setLevel(logging.WARNING)
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

        # Update collection counts
        Set.update_collection_counts()

        # Precalculate and cache set data
        sets_with_counts = Set.get_sets_with_collection_counts()
        sets_data = [
            set.to_dict()
            for set, _ in sets_with_counts
        ]
        sets_data = convert_decimal_to_float(sets_data)
        redis_client.set('sets_data', orjson.dumps(sets_data))

    # Register routes
    register_routes(app)

    # Add Redis client to app context
    app.redis_client = redis_client

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    return app

from flask.cli import FlaskGroup

cli = FlaskGroup(create_app=create_app)

if __name__ == '__main__':
    cli()

"""
To set up and run this application:

1. Create a virtual environment:
   python3 -m venv venv

2. Activate the virtual environment:
   source venv/bin/activate

3. Install the required packages:
   pip install -r requirements.txt

4. Set the FLASK_APP environment variable:
   export FLASK_APP=main.py

5. Run database migrations:
   flask db upgrade

6. Run the application:
   flask run
"""
