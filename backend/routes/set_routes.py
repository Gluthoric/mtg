from flask import Blueprint, jsonify, request, current_app
from models.set import Set
from models.card import Card
from models.set_collection_count import SetCollectionCount
from database import db
from sqlalchemy import asc, desc, func, Float, Integer, text
from sqlalchemy.orm import joinedload, subqueryload, load_only
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from decimal import Decimal
import orjson
import logging
from datetime import datetime

set_routes = Blueprint('set_routes', __name__, url_prefix='/api/sets')
logger = logging.getLogger(__name__)

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj



@set_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
    try:
        # Eagerly load related 'set' data to optimize queries
        query = Card.query.options(
            joinedload(Card.set)
        ).filter(Card.set_code == set_code)

        # Fetch all cards for the set without pagination
        cards = query.all()

        # Serialize card data
        cards_data = [card.to_dict() for card in cards]

        response = {
            'cards': cards_data,
            'total': len(cards_data)
        }

        return jsonify(response), 200
    except Exception as e:
        logger.exception(f"Error in get_set_cards: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the set cards."}), 500

from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import JSONB

@set_routes.route('/sets/<string:set_code>', methods=['GET'])
def get_collection_set_details(set_code):
    try:
        # Construct cache key
        cache_key = f"set_details:{set_code}"
        cached_data = current_app.redis_client.get(cache_key)

        if cached_data:
            return current_app.response_class(
                response=cached_data.decode(),
                status=200,
                mimetype='application/json'
            )

        # Fetch the set instance
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return jsonify({"error": "Set not found."}), 404

        # Query cards with necessary attributes
        query = Card.query.options(load_only(
            Card.id,
            Card.name,
            Card.type_line,
            Card.mana_cost,
            Card.rarity,
            Card.image_uris,
            Card.collector_number,
            Card.prices,
            Card.quantity_regular,
            Card.quantity_foil,
            Card.frame_effects,
            Card.promo_types,
            Card.promo,
            Card.reprint,
            Card.variation,
            Card.oversized
        )).filter(Card.set_code == set_code)

        cards = query.all()

        # Serialize cards
        cards_data = [card.to_dict() for card in cards]

        # Build response
        response = {
            'set': set_instance.to_dict(),
            'cards': cards_data,
            'total_cards': len(cards_data)
        }

        # Convert any Decimal objects to float
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500
