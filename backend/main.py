from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
from sqlalchemy import inspect, text

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    CORS(app)

    # Register routes
    register_routes(app)
    app.register_blueprint(set_routes, url_prefix='/api')

    return app

def alter_tables(app):
    with app.app_context():
        try:
            # Alter kiosk table
            db.session.execute(text("ALTER TABLE kiosk ALTER COLUMN id SET DEFAULT nextval('kiosk_id_seq'::regclass)"))
            db.session.execute(text("ALTER TABLE kiosk ALTER COLUMN id SET NOT NULL"))

            # Alter collections table
            db.session.execute(text("ALTER TABLE collections ALTER COLUMN id SET DEFAULT nextval('collections_id_seq'::regclass)"))
            db.session.execute(text("ALTER TABLE collections ALTER COLUMN id SET NOT NULL"))

            db.session.commit()
            print("Tables altered successfully.")
        except Exception as e:
            db.session.rollback()
            print(f"Error altering tables: {str(e)}")

def initialize_database(app):
    with app.app_context():
        inspector = inspect(db.engine)
        if not inspector.has_table("cards"):
            print("Creating database tables...")
            db.create_all()
            print("Database tables created.")
        else:
            print("Database tables already exist.")

        # Alter tables to add auto-increment
        alter_tables(app)

if __name__ == '__main__':
    app = create_app()

    # Initialize database (create tables if they don't exist and alter them)
    initialize_database(app)

    app.run(debug=True)