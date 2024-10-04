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

collection_routes = Blueprint('collection_routes', __name__)

@collection_routes.route('/collection', methods=['GET'])
@cache_response()
def get_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    set_code = request.args.get('set_code', '', type=str)

    query = Card.query

    if set_code:
        query = query.filter(Card.set_code == set_code)

    query = query.filter((Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0))

    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'collection': serialize_cards(collection.items, quantity_type='collection'),
        'total': collection.total,
        'pages': collection.pages,
        'current_page': page
    }

    return jsonify(result), 200

@collection_routes.route('/collection/sets', methods=['GET'])
@cache_response()
def get_collection_sets():
    try:
        name = request.args.get('name', type=str)
        set_types = request.args.getlist('set_type[]')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            return handle_error(400, f"Invalid sort_by field: {sort_by}")

        if sort_by == 'collection_count':
            sort_column = SetCollectionCount.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        order_func = desc if sort_order.lower() == 'desc' else asc

        value_subquery = (
            db.session.query(
                Card.set_code,
                func.sum(
                    (func.cast(Card.prices['usd'].astext, Float) * Card.quantity_collection_regular) +
                    (func.cast(Card.prices['usd_foil'].astext, Float) * Card.quantity_collection_foil)
                ).label('total_value')
            )
            .group_by(Card.set_code)
            .subquery()
        )

        query = (
            db.session.query(
                Set,
                func.coalesce(SetCollectionCount.collection_count, 0).label('collection_count'),
                func.coalesce(value_subquery.c.total_value, 0).label('total_value')
            )
            .join(SetCollectionCount, Set.code == SetCollectionCount.set_code)
            .outerjoin(value_subquery, Set.code == value_subquery.c.set_code)
        )

        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
        if set_types:
            query = query.filter(Set.set_type.in_(set_types))
        else:
            default_set_types = ['core', 'expansion', 'masters', 'draft_innovation', 'funny', 'commander']
            query = query.filter(Set.set_type.in_(default_set_types))

        query = query.order_by(order_func(sort_column))

        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)

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

        response = convert_decimals(response)

        return jsonify(response), 200
    except Exception as e:
        return handle_error(500, f"An unexpected error occurred: {str(e)}")

@collection_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    schema = UpdateCardSchema()
    errors = schema.validate(request.json)
    if errors:
        return handle_error(400, str(errors))

    data = schema.load(request.json)
    quantity_regular = data['quantity_regular']
    quantity_foil = data['quantity_foil']

    card = Card.query.get(card_id)
    if not card:
        return handle_error(404, "Card not found.")

    old_set_code = card.set_code
    card.quantity_collection_regular = quantity_regular
    card.quantity_collection_foil = quantity_foil

    db.session.commit()

    current_app.redis_client.delete(f"collection:set:{old_set_code}")
    current_app.redis_client.delete(f"collection_sets:{old_set_code}")
    current_app.redis_client.delete("collection_stats")

    return jsonify(card.to_dict()), 200

@collection_routes.route('/collection/stats', methods=['GET'])
@cache_response()
def get_collection_stats():
    return get_stats('quantity_collection_regular', 'quantity_collection_foil', 'collection_stats')

@collection_routes.route('/collection/sets/<string:set_code>/cards', methods=['GET'])
@cache_response()
def get_collection_set_cards(set_code):
    name = request.args.get('name', '', type=str)
    rarities = request.args.getlist('rarities') + request.args.getlist('rarities[]')
    colors = request.args.getlist('colors') + request.args.getlist('colors[]')
    types = request.args.getlist('types') + request.args.getlist('types[]')
    keyword = request.args.get('keyword', '', type=str)

    try:
        query = Card.query.filter(Card.set_code == set_code)

        if name:
            query = query.filter(Card.name.ilike(f'%{name}%'))
        if rarities:
            query = query.filter(Card.rarity.in_(rarities))
        if colors:
            query = query.filter(Card.colors.overlap(colors))
        if types:
            type_filters = [Card.type_line.ilike(f'%{type_}%') for type_ in types]
            query = query.filter(or_(*type_filters))
        if keyword:
            query = query.filter(Card.keywords.contains([keyword]))

        query = query.order_by(func.cast(func.regexp_replace(Card.collector_number, '[^0-9]', '', 'g'), db.Integer))

        cards = query.all()

        result = {
            'cards': [card.to_dict() for card in cards],
            'total': len(cards),
        }

        return jsonify(result), 200
    except Exception as e:
        return handle_error(500, f"An unexpected error occurred: {str(e)}")

@collection_routes.route('/collection/sets/<string:set_code>', methods=['GET'])
@cache_response()
def get_collection_set(set_code):
    try:
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return handle_error(404, "Set not found.")

        set_data = set_instance.to_dict()
        cards = Card.query.filter_by(set_code=set_code).all()
        set_data['cards'] = [card.to_dict() for card in cards]

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

        for card in cards:
            collection_count += card.quantity_collection_regular + card.quantity_collection_foil
            regular_value = float(card.prices.get('usd', 0) or 0) * card.quantity_collection_regular
            foil_value = float(card.prices.get('usd_foil', 0) or 0) * card.quantity_collection_foil
            total_value += regular_value + foil_value

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

        set_data['collection_count'] = collection_count
        set_data['collection_percentage'] = (collection_count / set_instance.card_count) * 100 if set_instance.card_count else 0
        set_data['total_value'] = round(total_value, 2)
        set_data['statistics'] = statistics

        return jsonify({
            "set": set_data,
            "cards": set_data['cards']
        }), 200
    except Exception as e:
        return handle_error(500, f"An error occurred while fetching the set: {str(e)}")
