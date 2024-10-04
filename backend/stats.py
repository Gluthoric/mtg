from typing import Dict, Any
from flask import current_app, jsonify
from models.card import Card
from sqlalchemy import func, Float
from database import db
import orjson
import logging

logger = logging.getLogger(__name__)

def get_stats(quantity_regular_field: str, quantity_foil_field: str, cache_key: str) -> Any:
    """
    Generic function to get stats for collection or kiosk.
    
    Args:
        quantity_regular_field (str): The field name for regular quantity.
        quantity_foil_field (str): The field name for foil quantity.
        cache_key (str): The cache key to use for Redis.
    
    Returns:
        flask.Response: A Flask response object containing the stats.
    """
    redis_client = current_app.redis_client
    cached_data = redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(
            func.sum(getattr(Card, quantity_regular_field) + getattr(Card, quantity_foil_field))
        ).scalar() or 0
        unique_cards = Card.query.filter(
            (getattr(Card, quantity_regular_field) > 0) | (getattr(Card, quantity_foil_field) > 0)
        ).count()

        total_value_query = db.session.query(
            func.sum(
                (func.cast(Card.prices['usd'].astext, Float) * getattr(Card, quantity_regular_field)) +
                (func.cast(Card.prices['usd_foil'].astext, Float) * getattr(Card, quantity_foil_field))
            )
        ).filter(
            (getattr(Card, quantity_regular_field) > 0) | (getattr(Card, quantity_foil_field) > 0)
        )
        total_value = total_value_query.scalar() or 0

        result: Dict[str, Any] = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result).decode()
        redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        logger.exception(f"Error getting stats for {cache_key}: {str(e)}")
        return jsonify({"error": str(e)}), 500
