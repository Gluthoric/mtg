from flask import Blueprint, jsonify, request, current_app
from models.set import Set
from models.card import Card
from models.set_collection_count import SetCollectionCount
from database import db
from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.exc import SQLAlchemyError
from collections import defaultdict
from decimal import Decimal
import orjson
import logging

set_routes = Blueprint('set_routes', __name__)
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

@set_routes.route('/sets', methods=['GET'])
def get_all_sets():
    try:
        # Extract query parameters
        name = request.args.get('name', type=str)
        set_types = request.args.getlist('set_type[]')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        # Construct cache key
        cache_key = f"collection_sets:name:{name}:set_type:{','.join(set_types)}:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
        cached_data = current_app.redis_client.get(cache_key)

        if cached_data:
            return current_app.response_class(
                response=cached_data.decode(),
                status=200,
                mimetype='application/json'
            )

        logger.info(f"Received parameters: name={name}, set_types={set_types}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Define valid sort fields and prevent SQL injection
        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(error_message)
            return jsonify({"error": error_message}), 400

        # Determine sort column
        if sort_by == 'collection_count':
            sort_column = SetCollectionCount.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        # Apply sort order
        order_func = desc if sort_order.lower() == 'desc' else asc

        # Build the main query to return Set instances
        query = db.session.query(Set)\
            .outerjoin(SetCollectionCount, Set.code == SetCollectionCount.set_code)\
            .options(
                subqueryload(Set.cards),  # Eagerly load related cards
                joinedload(Set.collection_count)  # Eagerly load collection_count
            )

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.info(f"Applied filter: Set.name ilike '%{name}%'")
        if set_types:
            query = query.filter(Set.set_type.in_(set_types))
            logger.info(f"Applied filter: Set.set_type IN {set_types}")
        else:
            # Use the partial index for relevant set types if no specific set_types are provided
            default_set_types = ['core', 'expansion', 'masters', 'draft_innovation', 'funny', 'commander']
            query = query.filter(Set.set_type.in_(default_set_types))
            logger.info("Applied filter: Using partial index for relevant set types")

        # Apply sorting
        query = query.order_by(order_func(sort_column))

        # Execute the query with pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

        sets_list = []
        for set_instance in paginated_sets.items:
            set_data = set_instance.to_dict()
            set_data['collection_count'] = set_instance.collection_count.collection_count if set_instance.collection_count else 0
            set_data['collection_percentage'] = (set_data['collection_count'] / set_instance.card_count) * 100 if set_instance.card_count else 0

            # Compute total_value and variants
            total_value = 0.0
            variants = defaultdict(list)
            for card in set_instance.cards:
                usd_price = float(card.prices.get('usd', 0)) if card.prices and 'usd' in card.prices else 0.0
                usd_foil_price = float(card.prices.get('usd_foil', 0)) if card.prices and 'usd_foil' in card.prices else 0.0
                total_value += (usd_price * card.quantity_collection_regular) + (usd_foil_price * card.quantity_collection_foil)

                # Categorize variant cards
                if card.frame_effects and 'showcase' in card.frame_effects:
                    category = 'Showcases'
                elif card.frame_effects and 'extendedart' in card.frame_effects:
                    category = 'Extended Art'
                elif card.promo_types and 'fracturefoil' in card.promo_types:
                    category = 'Fracture Foils'
                elif card.frame_effects and 'borderless' in card.frame_effects:
                    category = 'Borderless Cards'
                elif card.promo_types and 'promo' in card.promo_types:
                    category = 'Promos'
                else:
                    category = 'Art Variants'
                variants[category].append(card.to_dict())

            set_data['total_value'] = round(total_value, 2)
            set_data['variants'] = variants

            sets_list.append(set_data)

        # Convert Decimal objects to float if needed
        sets_list = convert_decimals(sets_list)

        response = {
            'sets': sets_list,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any remaining Decimal objects in the response
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

        logger.info(f"Returning response with {len(sets_list)} sets")
        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except ValueError as ve:
        logger.error(f"ValueError in get_all_sets: {str(ve)}")
        return jsonify({"error": str(ve)}), 400
    except SQLAlchemyError as sae:
        logger.error(f"SQLAlchemyError in get_all_sets: {str(sae)}")
        return jsonify({"error": "A database error occurred."}), 500
    except Exception as e:
        logger.exception(f"Unexpected error in get_all_sets: {str(e)}")
        return jsonify({"error": "An unexpected error occurred."}), 500

@set_routes.route('/sets/<string:set_code>', methods=['GET'])
def get_set(set_code):
    try:
        set_instance = Set.query.filter_by(code=set_code).first_or_404()
        return jsonify(set_instance.to_dict()), 200
    except Exception as e:
        logger.exception(f"Error in get_set: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the set."}), 500

@set_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
    try:
        # Extract filter parameters
        name_filter = request.args.get('name', '', type=str)
        rarity_filter = request.args.get('rarity', '', type=str)

        # Eagerly load related 'set' data to optimize queries
        query = Card.query.options(
            joinedload(Card.set)
        ).filter(Card.set_code == set_code)

        # Apply filters based on query parameters
        if name_filter:
            query = query.filter(Card.name.ilike(f'%{name_filter}%'))
        if rarity_filter:
            query = query.filter(Card.rarity == rarity_filter)

        # Fetch all matching cards without pagination
        cards = query.all()

        # Serialize card data
        cards_data = [card.to_dict() for card in cards]

        response = {
            'cards': cards_data,
            'total': len(cards_data),
            'pages': 1,
            'current_page': 1
        }

        return jsonify(response), 200
    except Exception as e:
        logger.exception(f"Error in get_set_cards: {str(e)}")
        return jsonify({"error": "An error occurred while fetching the set cards."}), 500
