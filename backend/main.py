from flask import Flask, jsonify, request
from flask_cors import CORS
from config import Config
from database import db
from routes import register_routes
from models.card import Card
from sqlalchemy.sql import func, text
import redis
import orjson

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def get_api_stats(app):
    def _get_stats():
        cache_key = "api_stats"
        force_refresh = request.args.get('refresh', '').lower() == 'true'

        if not force_refresh:
            cached_data = app.redis_client.get(cache_key)
            if cached_data:
                return app.response_class(
                    response=cached_data,
                    status=200,
                    mimetype='application/json'
                )

        try:
            # Collection stats
            collection_total = db.session.query(func.sum(Card.quantity_collection_regular + Card.quantity_collection_foil)).scalar() or 0
            collection_unique = Card.query.filter((Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0)).count()

            collection_value_query = text("""
                SELECT SUM(
                    (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_collection_regular) +
                    (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_collection_foil)
                )
                FROM cards
                WHERE quantity_collection_regular > 0 OR quantity_collection_foil > 0
            """)
            collection_value = db.session.execute(collection_value_query).scalar() or 0

            # Kiosk stats
            kiosk_total = db.session.query(func.sum(Card.quantity_kiosk_regular + Card.quantity_kiosk_foil)).scalar() or 0
            kiosk_unique = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).count()

            kiosk_value_query = text("""
                SELECT SUM(
                    (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_kiosk_regular) +
                    (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_kiosk_foil)
                )
                FROM cards
                WHERE quantity_kiosk_regular > 0 OR quantity_kiosk_foil > 0
            """)
            kiosk_value = db.session.execute(kiosk_value_query).scalar() or 0

            # Total stats
            total_cards = collection_total + kiosk_total
            total_unique = Card.query.filter(
                (Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0) |
                (Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)
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
            app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

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