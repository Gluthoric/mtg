from flask import Blueprint, send_from_directory, current_app
from .card_routes import card_routes
from .set_routes import set_routes
import os

def register_routes(app):
    api = Blueprint('api', __name__, url_prefix='/api')

    api.register_blueprint(card_routes)
    api.register_blueprint(set_routes)

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
