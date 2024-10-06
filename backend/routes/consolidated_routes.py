from flask import Blueprint, jsonify, request, current_app
from models.card import Card
from models.set import Set
from database import db
from sqlalchemy import or_
from utils import cache_response, serialize_cards
from errors import handle_error

consolidated_routes = Blueprint('consolidated_routes', __name__)

@consolidated_routes.route('/v2/cards', methods=['GET'])
@cache_response()
def get_cards_v2():
    set_code = request.args.get('set_code')
    source = request.args.get('source')
    include_set_details = request.args.get('include_set_details', 'false').lower() == 'true'
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Build the base query
    query = Card.query

    if set_code:
        query = query.filter(Card.set_code == set_code)

    if source == 'collection':
        query = query.filter((Card.quantity_regular > 0) | (Card.quantity_foil > 0))
    elif source == 'kiosk':
        query = query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0))

    # Add detailed logging to see the query before execution
    current_app.logger.info(f"Executing query: {query}")
    current_app.logger.info(f"Parameters - set_code: {set_code}, source: {source}, include_set_details: {include_set_details}, page: {page}, per_page: {per_page}")

    try:
        # Execute the query with pagination
        cards = query.paginate(page=page, per_page=per_page, error_out=False)

        # Logging for debugging purposes
        if not cards.items:
            current_app.logger.warning(f"No cards found for set_code={set_code} and source={source}")
        else:
            current_app.logger.info(f"Cards found: {len(cards.items)} for set_code={set_code} and source={source}")

        # Serialize cards
        result = {
            'cards': serialize_cards(cards.items, quantity_type=source if source else 'default'),
            'total': cards.total,
            'pages': cards.pages,
            'current_page': page
        }

        # Add set details if requested and available
        if include_set_details and set_code:
            set_instance = Set.query.filter_by(code=set_code).first()
            if set_instance:
                result['set_details'] = set_instance.to_dict()
            else:
                current_app.logger.warning(f"No set details found for set_code={set_code}")

        return jsonify(result), 200
    except Exception as e:
        current_app.logger.error(f"Error while executing query: {e}")
        return {"error": "An error occurred while fetching the cards."}, 500
