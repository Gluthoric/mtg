from flask import Flask, send_from_directory
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from database import db
from routes import register_routes
import redis
import orjson
import os

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def create_app():
    app = Flask(__name__, static_folder='../frontend/dist', static_url_path='')
    app.config.from_object(Config)
    app.config['SQLALCHEMY_ECHO'] = True

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

    # Serve static files from the Vue app's build directory
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(app.static_folder + '/' + path):
            return send_from_directory(app.static_folder, path)
        else:
            return send_from_directory(app.static_folder, 'index.html')

    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
