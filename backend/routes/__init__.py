from flask import Blueprint
from .card_routes import card_routes
from .set_routes import set_routes
from .collection_routes import collection_routes
from .kiosk_routes import kiosk_routes

def register_routes(app):
    api = Blueprint('api', __name__, url_prefix='/api')

    api.register_blueprint(card_routes, url_prefix='/cards')
    api.register_blueprint(set_routes, url_prefix='/sets')
    api.register_blueprint(collection_routes, url_prefix='/collection')
    api.register_blueprint(kiosk_routes, url_prefix='/kiosk')

    app.register_blueprint(api)

    @app.route('/')
    def index():
        return "Welcome to the MTG Collection Kiosk API"