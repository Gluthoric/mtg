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
from utils import cache_response, convert_decimals

set_routes = Blueprint('set_routes', __name__)
logger = logging.getLogger(__name__)



@set_routes.route('/<string:set_code>/cards', methods=['GET'])
@cache_response()
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

        return response, 200  # Correct variable name
    except Exception as e:
        logger.exception(f"Error in get_set_cards: {str(e)}")
        return {"error": "An error occurred while fetching the set cards."}, 500

from sqlalchemy import func, text
from sqlalchemy.dialects.postgresql import JSONB


@set_routes.route('/<string:set_code>/details', methods=['GET'])
@cache_response()
def get_collection_set_details(set_code):
    try:
        logger.info(f"Fetching details for set with code: {set_code}")
        # Fetch the set instance
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            logger.warning(f"Set with code {set_code} not found")
            return {"error": "Set not found."}, 404

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

        return response, 200  # Correct variable name
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return {"error": error_message}, 500


@set_routes.route('/<string:set_code>', methods=['GET'])
@cache_response()
def get_set(set_code):
    try:
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return {"error": "Set not found."}, 404

        set_data = set_instance.to_dict()

        # Fetch cards for this set
        cards = Card.query.filter_by(set_code=set_code).all()
        cards_data = [card.to_dict() for card in cards]

        response = {
            "set": set_data,
            "cards": cards_data
        }

        return response, 200  # Return as a tuple
    except Exception as e:
        error_message = f"An error occurred while fetching the set: {str(e)}"
        logger.exception(error_message)
        return {"error": error_message}, 500

@set_routes.route('/api/sets/<string:set_code>', methods=['GET'])
@cache_response()
def get_set_api(set_code):
    response = get_set(set_code)
    return response[0], response[1]
