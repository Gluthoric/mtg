from flask import Blueprint, jsonify, request, current_app
from models.card import Card
from models.set import Set
from models.set_collection_count import SetCollectionCount
from database import db
from sqlalchemy import func, or_, Float, distinct, text
from sqlalchemy.sql import asc, desc
from utils import safe_float, convert_decimals, cache_response, serialize_cards
from errors import handle_error
from schemas import UpdateCardSchema
from stats import get_stats
import logging

logger = logging.getLogger(__name__)

collection_routes = Blueprint('collection_routes', __name__)

@collection_routes.route('/collection', methods=['GET'])
@cache_response()
def get_collection():
    # Get pagination parameters from the request
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    set_code = request.args.get('set_code', '', type=str)

    # Base query to get cards
    query = Card.query

    # Filter by set code if provided
    if set_code:
        query = query.filter(Card.set_code == set_code)

    # Only include cards that have quantity greater than zero in either regular or foil
    query = query.filter((Card.quantity_regular > 0) | (Card.quantity_foil > 0))

    # Paginate the results
    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    # Serialize the collection to return as a response
    result = {
        'collection': serialize_cards(collection.items, quantity_type='collection'),
        'total': collection.total,
        'pages': collection.pages,
        'current_page': page
    }

    return result, 200

@collection_routes.route('/collection/sets', methods=['GET'])
@cache_response()
def get_collection_sets():
    try:
        # Extract query parameters from the request
        name = request.args.get('name', type=str)
        set_types = request.args.getlist('set_type[]')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        # Log received parameters for debugging purposes
        logger.info(f"get_collection_sets: Received parameters: name={name}, set_types={set_types}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Define valid sort fields to prevent SQL injection
        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(f"get_collection_sets: {error_message}")
            return {"error": error_message}, 400

        # Determine the sorting column based on the sort_by parameter
        if sort_by == 'collection_count':
            sort_column = SetCollectionCount.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        # Determine sort order (ascending or descending)
        order_func = desc if sort_order.lower() == 'desc' else asc

        # Create a subquery to calculate the total value of cards in each set
        value_subquery = (
            db.session.query(
                Card.set_code,
                func.sum(
                    (func.cast(Card.prices['usd'].astext, Float) * Card.quantity_regular) +
                    (func.cast(Card.prices['usd_foil'].astext, Float) * Card.quantity_foil)
                ).label('total_value')
            )
            .group_by(Card.set_code)
            .subquery()
        )

        # Main query to get sets and their collection count and total value
        query = (
            db.session.query(
                Set,
                func.coalesce(SetCollectionCount.collection_count, 0).label('collection_count'),
                func.coalesce(value_subquery.c.total_value, 0).label('total_value')
            )
            .join(SetCollectionCount, Set.code == SetCollectionCount.set_code)
            .outerjoin(value_subquery, Set.code == value_subquery.c.set_code)
        )

        # Apply filters based on the query parameters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.debug(f"get_collection_sets: Applied filter: Set.name ilike '%{name}%'")
        if set_types:
            query = query.filter(Set.set_type.in_(set_types))
            logger.debug(f"get_collection_sets: Applied filter: Set.set_type IN {set_types}")
        else:
            # Use default set types if none are provided
            default_set_types = ['core', 'expansion', 'masters', 'draft_innovation', 'funny', 'commander']
            query = query.filter(Set.set_type.in_(default_set_types))
            logger.debug("get_collection_sets: Applied filter: Using partial index for relevant set types")

        # Apply sorting based on the sort column and order
        query = query.order_by(order_func(sort_column))

        # Execute the query with pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"get_collection_sets: Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

        # Process results and serialize the set data
        sets_list = []
        for set_instance, collection_count, total_value in paginated_sets.items:
            set_data = set_instance.to_dict()
            set_data['collection_count'] = collection_count
            set_data['collection_percentage'] = (collection_count / set_instance.card_count) * 100 if set_instance.card_count else 0
            set_data['total_value'] = round(total_value, 2)
            sets_list.append(set_data)

        response = {
            'sets': sets_list,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any Decimal objects in the response to float
        response = convert_decimals(response)

        logger.info(f"Returning response with {len(sets_list)} sets")
        return response, 200  # Return data directly
    except Exception as e:
        error_message = f"An unexpected error occurred in get_collection_sets: {str(e)}"
        logger.exception(error_message)
        return {"error": "An internal server error occurred. Please try again later."}, 500

@collection_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    # Validate request data using schema
    schema = UpdateCardSchema()
    errors = schema.validate(request.json)
    if errors:
        return jsonify({"error": errors}), 400

    # Load the validated data
    data = schema.load(request.json)
    quantity_regular = data['quantity_regular']
    quantity_foil = data['quantity_foil']

    # Fetch the card from the database
    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    # Update the card quantities
    old_set_code = card.set_code
    card.quantity_regular = quantity_regular
    card.quantity_foil = quantity_foil

    # Commit the changes to the database
    db.session.commit()

    # Invalidate specific caches to ensure data consistency
    current_app.redis_client.delete(f"collection:set:{old_set_code}")
    current_app.redis_client.delete(f"collection_sets:{old_set_code}")
    current_app.redis_client.delete("collection_stats")

    # Serialize updated card data
    card_data = card.to_dict()

    return current_app.response_class(
        response=current_app.json.dumps(card_data),
        status=200,
        mimetype='application/json'
    )

@collection_routes.route('/collection/stats', methods=['GET'])
@cache_response()
def get_collection_stats():
    # Return collection statistics using predefined keys
    return get_stats('quantity_collection_regular', 'quantity_collection_foil', 'collection_stats')

@collection_routes.route('/collection/sets/<string:set_code>/cards', methods=['GET'])
@cache_response()
def get_collection_set_cards(set_code):
    # Extract query parameters from the request
    name = request.args.get('name', '', type=str)
    rarities = request.args.getlist('rarities') + request.args.getlist('rarities[]')
    colors = request.args.getlist('colors') + request.args.getlist('colors[]')
    types = request.args.getlist('types') + request.args.getlist('types[]')
    keyword = request.args.get('keyword', '', type=str)

    try:
        # Base query to get cards from a specific set
        query = Card.query.filter(Card.set_code == set_code)

        # Apply filters if provided
        if name:
            query = query.filter(Card.name.ilike(f'%{name}%'))
        if rarities:
            query = query.filter(Card.rarity.in_(rarities))
        if colors:
            # Define valid colors and ensure there are no invalid values
            VALID_COLORS = {'W', 'U', 'B', 'R', 'G', 'C'}
            invalid_colors = set(colors) - VALID_COLORS
            if invalid_colors:
                return jsonify({"error": f"Invalid colors: {', '.join(invalid_colors)}"}), 400

            # Handle "C" for colorless cards
            if 'C' in colors:
                colors.remove('C')
                # Filter for colorless cards where the 'colors' array is empty
                colorless_filter = func.jsonb_array_length(Card.colors) == 0
            else:
                colorless_filter = None

            # Build the colors filter for colored cards
            if colors:
                colors_filter = Card.colors.overlap(colors)
                if colorless_filter is not None:
                    final_colors_filter = or_(colors_filter, colorless_filter)
                else:
                    final_colors_filter = colors_filter
            else:
                # Only colorless cards are selected
                final_colors_filter = colorless_filter

            # Apply the final colors filter
            if final_colors_filter is not None:
                query = query.filter(final_colors_filter)
        if types:
            # Create filters for card types
            type_filters = [Card.type_line.ilike(f'%{type_}%') for type_ in types]
            query = query.filter(or_(*type_filters))
        if keyword:
            # Filter based on keyword presence in card keywords
            query = query.filter(Card.keywords.contains([keyword]))

        # Order cards by their collector number, converting to an integer to ensure proper sorting
        query = query.order_by(func.cast(func.regexp_replace(Card.collector_number, '[^0-9]', '', 'g'), db.Integer))

        # Fetch all cards matching the filters
        cards = query.all()

        # Serialize the result
        result = {
            'cards': [card.to_dict() for card in cards],
            'total': len(cards),
        }

        return jsonify(result), 200
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

@collection_routes.route('/collection/sets/<string:set_code>', methods=['GET'])
@cache_response()
def get_collection_set(set_code):
    try:
        # Fetch the set instance by set code
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return {"error": "Set not found."}, 404

        # Serialize set data
        set_data = set_instance.to_dict()

        # Fetch cards for this set
        cards = Card.query.filter_by(set_code=set_code).all()
        set_data['cards'] = [card.to_dict() for card in cards]

        # Initialize statistics dictionary
        statistics = {
            'frame_effects': {},
            'promo_types': {},
            'other_attributes': {
                'promo': 0,
                'reprint': 0,
                'variation': 0,
                'oversized': 0
            }
        }

        collection_count = 0
        total_value = 0.0

        # Calculate collection statistics and card values
        for card in cards:
            collection_count += card.quantity_collection_regular + card.quantity_collection_foil

            # Calculate total value for regular and foil cards
            regular_value = float(card.prices.get('usd', 0) or 0) * card.quantity_collection_regular
            foil_value = float(card.prices.get('usd_foil', 0) or 0) * card.quantity_collection_foil
            total_value += regular_value + foil_value

            # Update statistics for frame effects, promo types, and other attributes
            if card.frame_effects:
                for effect in card.frame_effects:
                    statistics['frame_effects'][effect] = statistics['frame_effects'].get(effect, 0) + 1
            if card.promo_types:
                for promo_type in card.promo_types:
                    statistics['promo_types'][promo_type] = statistics['promo_types'].get(promo_type, 0) + 1
            if card.promo:
                statistics['other_attributes']['promo'] += 1
            if card.reprint:
                statistics['other_attributes']['reprint'] += 1
            if card.variation:
                statistics['other_attributes']['variation'] += 1
            if card.oversized:
                statistics['other_attributes']['oversized'] += 1

        # Update set data with collection count, percentage, total value, and statistics
        set_data['collection_count'] = collection_count
        set_data['collection_percentage'] = (collection_count / set_instance.card_count) * 100 if set_instance.card_count else 0
        set_data['total_value'] = round(total_value, 2)
        set_data['statistics'] = statistics

        response = {
            "set": set_data,
            "cards": set_data['cards']
        }

        return response, 200  # Return data directly
    except Exception as e:
        error_message = f"An error occurred while fetching the set: {str(e)}"
        logger.exception(error_message)
        return {"error": error_message}, 500
