from flask import Blueprint
from .card_routes import card_routes
from .set_routes import set_routes

def register_routes(app):
    api = Blueprint('api', __name__, url_prefix='/api')

    api.register_blueprint(card_routes)
    api.register_blueprint(set_routes)

    app.register_blueprint(api)

    @app.route('/')
    def index():
        return "Welcome to the MTG Collection Kiosk API"