from flask import Blueprint, jsonify, request, current_app
from models.card import Card
from sqlalchemy import or_
from sqlalchemy.orm import load_only, joinedload
import orjson
import logging
from utils import cache_response
from errors import handle_error, APIError
from schemas import CardSearchSchema
from flasgger import swag_from

logger = logging.getLogger(__name__)

card_routes = Blueprint('card_routes', __name__)

@card_routes.errorhandler(APIError)
def handle_api_error(error):
    return handle_error(error.status_code, error.message, error.error_type)

@card_routes.route('/cards', methods=['GET'])
@cache_response()
@swag_from({
    'tags': ['Cards'],
    'summary': 'Get a list of cards',
    'parameters': [
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'default': 1,
            'description': 'Page number'
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'default': 50,
            'description': 'Number of items per page'
        },
        {
            'name': 'name',
            'in': 'query',
            'type': 'string',
            'description': 'Filter cards by name'
        },
        {
            'name': 'set_code',
            'in': 'query',
            'type': 'string',
            'description': 'Filter cards by set code'
        },
        {
            'name': 'rarity',
            'in': 'query',
            'type': 'string',
            'description': 'Filter cards by rarity'
        },
        {
            'name': 'colors',
            'in': 'query',
            'type': 'string',
            'description': 'Filter cards by colors (comma-separated)'
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response',
            'schema': {
                'type': 'object',
                'properties': {
                    'cards': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'name': {'type': 'string'},
                                'set_name': {'type': 'string'},
                                'set_code': {'type': 'string'},
                                'collector_number': {'type': 'string'},
                                'rarity': {'type': 'string'},
                                'image_uris': {'type': 'object'},
                                'prices': {'type': 'object'}
                            }
                        }
                    },
                    'total': {'type': 'integer'},
                    'pages': {'type': 'integer'},
                    'current_page': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': 'Bad request',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_cards():
    schema = CardSearchSchema()
    errors = schema.validate(request.args)
    if errors:
        return handle_error(400, str(errors))

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    name = request.args.get('name', '')
    set_code = request.args.get('set_code', '')
    rarity = request.args.get('rarity', '')
    colors = request.args.get('colors', '').split(',') if request.args.get('colors') else []

    query = Card.query

    if name:
        query = query.filter(Card.name.ilike(f'%{name}%'))
    if set_code:
        query = query.filter(Card.set_code == set_code)
    if rarity:
        query = query.filter(Card.rarity == rarity)
    if colors:
        query = query.filter(Card.colors.contains(colors))

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    response = {
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }

    return response, 200  # Let the decorator handle serialization and caching

@card_routes.route('/keywords', methods=['GET'])
@cache_response()
@swag_from({
    'tags': ['Cards'],
    'summary': 'Get a list of all keywords',
    'responses': {
        200: {
            'description': 'Successful response',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'string'
                }
            }
        }
    }
})
def get_keywords():
    # Query distinct keywords from the Card model
    keywords = db.session.query(Card.keywords).distinct().all()
    # Flatten the list of keywords
    all_keywords = set(keyword for sublist in keywords for keyword in sublist[0] if sublist[0])
    return jsonify(list(all_keywords)), 200

@card_routes.route('/cards/<string:card_id>', methods=['GET'])
@cache_response()
@swag_from({
    'tags': ['Cards'],
    'summary': 'Get a specific card by ID',
    'parameters': [
        {
            'name': 'card_id',
            'in': 'path',
            'type': 'string',
            'required': True,
            'description': 'Unique identifier of the card'
        }
    ],
    'responses': {
        200: {
            'description': 'Successful response',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'name': {'type': 'string'},
                    'set_name': {'type': 'string'},
                    'set_code': {'type': 'string'},
                    'collector_number': {'type': 'string'},
                    'type_line': {'type': 'string'},
                    'rarity': {'type': 'string'},
                    'mana_cost': {'type': 'string'},
                    'cmc': {'type': 'number'},
                    'oracle_text': {'type': 'string'},
                    'colors': {'type': 'array', 'items': {'type': 'string'}},
                    'image_uris': {'type': 'object'},
                    'prices': {'type': 'object'},
                    'quantity_regular': {'type': 'integer'},
                    'quantity_foil': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Card not found',
            'schema': {
                'type': 'object',
                'properties': {
                    'error': {'type': 'string'}
                }
            }
        }
    }
})
def get_card(card_id):
    # Fetch card from database, with optimization to load only the required fields
    card = Card.query.options(
        load_only(
            Card.id,
            Card.name,
            Card.image_uris,
            Card.collector_number,
            Card.prices,
            Card.rarity,
            Card.set_name,
            Card.set_code,
            Card.type_line,
            Card.mana_cost,
            Card.cmc,
            Card.oracle_text,
            Card.colors,
            Card.quantity_regular,
            Card.quantity_foil,
            Card.quantity_kiosk_regular,
            Card.quantity_kiosk_foil,
            Card.frame_effects,
            Card.promo_types,
            Card.promo,
            Card.reprint,
            Card.variation,
            Card.oversized,
            Card.keywords
        )
    ).filter_by(id=card_id).first()

    if not card:
        return {"error": "Card not found."}, 404

    # Serialize card data
    card_data = card.to_dict()

    return card_data, 200  # Let the decorator handle serialization and caching

@card_routes.route('/cards/bulk', methods=['POST'])
def get_bulk_cards():
    data = request.json
    card_ids = data.get('card_ids', [])
    if not card_ids:
        return jsonify({"error": "No card IDs provided."}), 400

    # Check if cards are already in cache
    cards_data = []
    card_ids_to_query = []
    for card_id in card_ids:
        cached_card = current_app.redis_client.get(f"card:{card_id}")
        if cached_card:
            cards_data.append(orjson.loads(cached_card))
        else:
            card_ids_to_query.append(card_id)

    # Fetch cards from database that were not in cache
    if card_ids_to_query:
        cards = Card.query.options(
            load_only(
                Card.id,
                Card.name,
                Card.image_uris,
                Card.collector_number,
                Card.prices,
                Card.rarity,
                Card.set_name,
                Card.set_code,
                Card.type_line,
                Card.mana_cost,
                Card.cmc,
                Card.oracle_text,
                Card.colors,
                Card.quantity_collection_regular,
                Card.quantity_collection_foil,
                Card.quantity_kiosk_regular,
                Card.quantity_kiosk_foil,
                Card.frame_effects,
                Card.promo_types,
                Card.promo,
                Card.reprint,
                Card.variation,
                Card.oversized,
                Card.keywords
            )
        ).filter(Card.id.in_(card_ids_to_query)).all()

        for card in cards:
            serialized_card = orjson.dumps(card.to_dict()).decode()
            # Cache each card for 5 minutes
            current_app.redis_client.setex(f"card:{card.id}", 300, serialized_card)
            cards_data.append(card.to_dict())

    return jsonify({"cards": cards_data}), 200

@card_routes.route('/cards/search', methods=['GET'])
def search_cards():
    query_param = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Card.query.options(load_only(
        Card.id, Card.name, Card.set_name, Card.set_code, Card.collector_number,
        Card.type_line, Card.rarity, Card.mana_cost, Card.cmc, Card.oracle_text,
        Card.colors, Card.image_uris, Card.prices, Card.quantity_collection_regular,
        Card.quantity_collection_foil, Card.quantity_kiosk_regular, Card.quantity_kiosk_foil,
        Card.frame_effects, Card.promo_types, Card.promo, Card.reprint, Card.variation,
        Card.oversized, Card.keywords
    )).filter(
        or_(
            Card.name.ilike(f'%{query_param}%'),
            Card.type_line.ilike(f'%{query_param}%'),
            Card.oracle_text.ilike(f'%{query_param}%')
        )
    )

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200

@card_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
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

        return response, 200  # Return data directly
    except Exception as e:
        logger.exception(f"Error in get_set_cards: {str(e)}")
        return {"error": "An error occurred while fetching the set cards."}, 500

@card_routes.route('/cache_stats', methods=['GET'])
def get_cache_stats():
    total_calls = int(current_app.redis_client.get('cache_total_calls') or 0)
    hits = int(current_app.redis_client.get('cache_hits') or 0)
    misses = int(current_app.redis_client.get('cache_misses') or 0)

    hit_rate = (hits / total_calls * 100) if total_calls > 0 else 0

    response_times = current_app.redis_client.lrange('cache_response_times', 0, -1)
    avg_response_time = sum(float(t) for t in response_times) / len(response_times) if response_times else 0

    return jsonify({
        'total_calls': total_calls,
        'hits': hits,
        'misses': misses,
        'hit_rate': f"{hit_rate:.2f}%",
        'avg_response_time': f"{avg_response_time:.4f} seconds"
    })
