from flask import Blueprint, send_from_directory, current_app
import os
from .card_routes import card_routes
from .collection_routes import collection_routes
from .kiosk_routes import kiosk_routes
from .set_routes import set_routes
from .import_routes import import_routes

def register_routes(app):
    api = Blueprint('api', __name__, url_prefix='/api')

    api.register_blueprint(card_routes)
    api.register_blueprint(collection_routes)
    api.register_blueprint(kiosk_routes)
    api.register_blueprint(set_routes)
    api.register_blueprint(import_routes)

    app.register_blueprint(api)

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        if path != "" and os.path.exists(os.path.join(current_app.static_folder, path)):
            return send_from_directory(current_app.static_folder, path)
        else:
            return send_from_directory(current_app.static_folder, 'index.html')

    # Add a catch-all route to handle Vue.js routing
    @app.errorhandler(404)
    def not_found(error):
        return send_from_directory(current_app.static_folder, 'index.html')
