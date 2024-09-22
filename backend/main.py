from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from routes.set_routes import set_routes  # Import the new blueprint
from sqlalchemy import inspect

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register routes
    register_routes(app)
    app.register_blueprint(set_routes, url_prefix='/api')  # Register with /api prefix

    return app

def initialize_database(app):
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("cards"):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created.")
        else:
            print("Database tables already exist.")

if __name__ == '__main__':
    app = create_app()

    # Initialize database (create tables only if they don't exist)
    initialize_database(app)

    app.run(debug=True)