from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from routes.set_routes import set_routes
from routes.kiosk_routes import kiosk_routes
from routes.collection_routes import collection_routes
from models.collection import Collection
from models.kiosk import Kiosk
from models.card import Card
from sqlalchemy.sql import func, text
import redis
import orjson

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_api_stats(app):
    def _get_stats():
        cache_key = "api_stats"
        cached_data = app.redis_client.get(cache_key)

        if cached_data:
            return app.response_class(
                response=cached_data,
                status=200,
                mimetype='application/json'
            )

        try:
            # Collection stats
            collection_total = db.session.query(func.sum(Collection.quantity_regular + Collection.quantity_foil)).scalar() or 0
            collection_unique = Collection.query.count()

            collection_value_query = text("""
                SELECT SUM(
                    (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * collections.quantity_regular) +
                    (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * collections.quantity_foil)
                )
                FROM collections
                JOIN cards ON cards.id = collections.card_id
            """)
            collection_value = db.session.execute(collection_value_query).scalar() or 0

            # Kiosk stats
            kiosk_total = db.session.query(func.sum(Kiosk.quantity_regular + Kiosk.quantity_foil)).scalar() or 0
            kiosk_unique = Kiosk.query.count()

            kiosk_value_query = text("""
                SELECT SUM(
                    (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * kiosk.quantity_regular) +
                    (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * kiosk.quantity_foil)
                )
                FROM kiosk
                JOIN cards ON cards.id = kiosk.card_id
            """)
            kiosk_value = db.session.execute(kiosk_value_query).scalar() or 0

            # Total stats
            total_cards = collection_total + kiosk_total
            total_unique = db.session.query(Card).filter(
                (Card.id.in_(db.session.query(Collection.card_id))) |
                (Card.id.in_(db.session.query(Kiosk.card_id)))
            ).count()
            total_value = collection_value + kiosk_value

            result = {
                'collection': {
                    'total_cards': int(collection_total),
                    'unique_cards': collection_unique,
                    'total_value': round(collection_value, 2)
                },
                'kiosk': {
                    'total_cards': int(kiosk_total),
                    'unique_cards': kiosk_unique,
                    'total_value': round(kiosk_value, 2)
                },
                'total': {
                    'total_cards': int(total_cards),
                    'unique_cards': total_unique,
                    'total_value': round(total_value, 2)
                }
            }

            serialized_data = orjson.dumps(result)
            app.redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

            return app.response_class(
                response=serialized_data,
                status=200,
                mimetype='application/json'
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return _get_stats

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
    app.register_blueprint(collection_routes, url_prefix='/api')

    # Add Redis client to app context
    app.redis_client = redis_client

    # Use orjson for JSON serialization
    app.json_encoder = orjson.dumps
    app.json_decoder = orjson.loads

    # Register the /api/stats endpoint
    app.add_url_rule('/api/stats', 'get_api_stats', get_api_stats(app), methods=['GET'])

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)