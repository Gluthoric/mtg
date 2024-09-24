from flask import Flask
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
from routes.kiosk_routes import kiosk_routes

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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)