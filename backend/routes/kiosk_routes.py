from flask import Blueprint, jsonify, request, current_app
from models.card import Card
from models.set import Set
from database import db
from sqlalchemy import func, distinct, text
from utils import safe_float, convert_decimals, cache_response, serialize_cards
from errors import handle_error
from schemas import UpdateCardSchema

kiosk_routes = Blueprint('kiosk_routes', __name__)

@kiosk_routes.route('/kiosk', methods=['GET'])
@cache_response()
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    kiosk = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'kiosk': serialize_cards(kiosk.items, quantity_type='kiosk'),
        'total': kiosk.total,
        'pages': kiosk.pages,
        'current_page': page
    }

    return jsonify(result), 200

@kiosk_routes.route('/kiosk/sets', methods=['GET'])
@cache_response()
def get_kiosk_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sortBy', 'released_at')
    sort_order = request.args.get('sortOrder', 'desc')

    try:
        kiosk_sets = db.session.query(Set).\
            join(Card, Card.set_code == Set.code).\
            filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
            distinct()

        if sort_by == 'released_at':
            kiosk_sets = kiosk_sets.order_by(Set.released_at.desc() if sort_order == 'desc' else Set.released_at)
        else:
            kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by).desc() if sort_order == 'desc' else getattr(Set, sort_by))

        paginated_sets = kiosk_sets.paginate(page=page, per_page=per_page, error_out=False)

        sets_data = []
        for set_obj in paginated_sets.items:
            set_dict = set_obj.to_dict()

            kiosk_count = db.session.query(func.count(distinct(Card.id))).\
                filter(Card.set_code == set_obj.code).\
                filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
                scalar()

            kiosk_percentage = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

            total_value_query = text("""
                SELECT SUM(
                    (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_kiosk_regular) +
                    (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_kiosk_foil)
                )
                FROM cards
                WHERE set_code = :set_code AND (quantity_kiosk_regular > 0 OR quantity_kiosk_foil > 0)
            """)
            total_value = db.session.execute(total_value_query, {'set_code': set_obj.code}).scalar() or 0.0

            set_dict['kiosk_count'] = kiosk_count
            set_dict['kiosk_percentage'] = kiosk_percentage
            set_dict['total_value'] = round(total_value, 2)

            sets_data.append(set_dict)

        sets_data = convert_decimals(sets_data)

        response = {
            'sets': sets_data,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        response = convert_decimals(response)

        return jsonify(response), 200
    except Exception as e:
        return handle_error(500, f"An unexpected error occurred: {str(e)}")

@kiosk_routes.route('/kiosk/sets/<string:set_code>/cards', methods=['GET'])
@cache_response()
def get_kiosk_set_cards(set_code):
    name_filter = request.args.get('name', '')
    rarity_filter = request.args.get('rarity', '')
    sort_by = request.args.get('sortBy', 'name')
    sort_order = request.args.get('sortOrder', 'asc')

    query = Card.query.filter(Card.set_code == set_code).filter(
        (Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)
    )

    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))
    if rarity_filter:
        query = query.filter(Card.rarity == rarity_filter)

    if sort_order == 'desc':
        query = query.order_by(getattr(Card, sort_by).desc())
    else:
        query = query.order_by(getattr(Card, sort_by))

    cards = query.all()
    cards_data = serialize_cards(cards, quantity_type='kiosk')

    set_instance = Set.query.filter_by(code=set_code).first()
    set_name = set_instance.name if set_instance else ''

    result = {
        'cards': cards_data,
        'set_name': set_name
    }

    return jsonify(result), 200

@kiosk_routes.route('/kiosk/<string:card_id>', methods=['POST', 'PUT'])
def update_kiosk(card_id):
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

    card.quantity_kiosk_regular = quantity_regular
    card.quantity_kiosk_foil = quantity_foil

    db.session.commit()

    current_app.redis_client.delete("kiosk:*")
    current_app.redis_client.delete("kiosk_sets:*")
    current_app.redis_client.delete(f"kiosk_set_cards:{card.set_code}:*")

    return jsonify(card.to_dict()), 200

@kiosk_routes.route('/kiosk/stats', methods=['GET'])
@cache_response()
def get_kiosk_stats():
    try:
        total_cards = db.session.query(func.sum(Card.quantity_kiosk_regular + Card.quantity_kiosk_foil)).scalar() or 0
        unique_cards = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).count()

        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_kiosk_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_kiosk_foil)
            )
            FROM cards
            WHERE quantity_kiosk_regular > 0 OR quantity_kiosk_foil > 0
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        return jsonify(result), 200
    except Exception as e:
        return handle_error(500, f"An unexpected error occurred: {str(e)}")
