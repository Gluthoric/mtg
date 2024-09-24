from flask import Blueprint, jsonify, request, current_app
from models.kiosk import Kiosk
from models.card import Card
from models.set import Set
from database import db
from sqlalchemy.sql import func, text
from sqlalchemy import distinct
import orjson

kiosk_routes = Blueprint('kiosk_routes', __name__)

def serialize_sets(sets):
    return [set_obj.to_dict() for set_obj in sets]

def serialize_cards(cards):
    return [{**card.to_dict(), 'quantity': kiosk_item.to_dict()} for card, kiosk_item in cards]

@kiosk_routes.route('/kiosk', methods=['GET'])
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cache_key = f"kiosk:page:{page}:per_page:{per_page}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    kiosk = Kiosk.query.join(Card).paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'kiosk': [
            {**item.card.to_dict(), 'quantity': item.to_dict()}
            for item in kiosk.items
        ],
        'total': kiosk.total,
        'pages': kiosk.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@kiosk_routes.route('/kiosk/sets', methods=['GET'])
def get_kiosk_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sortBy', 'released_at')
    sort_order = request.args.get('sortOrder', 'desc')

    cache_key = f"kiosk_sets:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    kiosk_sets = db.session.query(Set).\
        join(Card, Card.set_code == Set.code).\
        join(Kiosk, Kiosk.card_id == Card.id).\
        filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0)).\
        distinct()

    if sort_order == 'desc':
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by).desc())
    else:
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by))

    paginated_sets = kiosk_sets.paginate(page=page, per_page=per_page, error_out=False)

    sets_data = []
    for set_obj in paginated_sets.items:
        set_dict = set_obj.to_dict()

        kiosk_count = db.session.query(func.count(distinct(Card.id))).\
            join(Kiosk, Kiosk.card_id == Card.id).\
            filter(Card.set_code == set_obj.code).\
            filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0)).\
            scalar()

        set_dict['kiosk_count'] = kiosk_count
        set_dict['kiosk_percentage'] = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

        sets_data.append(set_dict)

    result = {
        'sets': sets_data,
        'total': paginated_sets.total,
        'pages': paginated_sets.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 600, serialized_data)  # Cache for 10 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@kiosk_routes.route('/kiosk/sets/<string:set_code>/cards', methods=['GET'])
def get_kiosk_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name_filter = request.args.get('name', '')
    rarity_filter = request.args.get('rarity', '')
    sort_by = request.args.get('sortBy', 'name')
    sort_order = request.args.get('sortOrder', 'asc')

    cache_key = f"kiosk_set_cards:{set_code}:page:{page}:per_page:{per_page}:name:{name_filter}:rarity:{rarity_filter}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    query = db.session.query(Card, Kiosk).\
        join(Kiosk, Kiosk.card_id == Card.id).\
        filter(Card.set_code == set_code).\
        filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0))

    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))
    if rarity_filter:
        query = query.filter(Card.rarity == rarity_filter)

    if sort_order == 'desc':
        query = query.order_by(getattr(Card, sort_by).desc())
    else:
        query = query.order_by(getattr(Card, sort_by))

    paginated_cards = query.paginate(page=page, per_page=per_page, error_out=False)

    cards_data = []
    for card, kiosk_item in paginated_cards.items:
        card_dict = card.to_dict()
        card_dict['quantity'] = kiosk_item.to_dict()
        cards_data.append(card_dict)

    set_name = Set.query.filter_by(code=set_code).first().name

    result = {
        'cards': cards_data,
        'set_name': set_name,
        'total': paginated_cards.total,
        'pages': paginated_cards.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@kiosk_routes.route('/kiosk/<string:card_id>', methods=['POST', 'PUT'])
def update_kiosk(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    kiosk_item = Kiosk.query.filter_by(card_id=card_id).first()

    if kiosk_item:
        kiosk_item.quantity_regular = quantity_regular
        kiosk_item.quantity_foil = quantity_foil
    else:
        kiosk_item = Kiosk(card_id=card_id, quantity_regular=quantity_regular, quantity_foil=quantity_foil)
        db.session.add(kiosk_item)

    db.session.commit()

    # Invalidate related caches
    current_app.redis_client.delete("kiosk:*")
    current_app.redis_client.delete("kiosk_sets:*")
    current_app.redis_client.delete(f"kiosk_set_cards:{kiosk_item.card.set_code}:*")

    return current_app.response_class(
        response=orjson.dumps(kiosk_item.to_dict()),
        status=200,
        mimetype='application/json'
    )

@kiosk_routes.route('/kiosk/<string:card_id>', methods=['DELETE'])
def remove_from_kiosk(card_id):
    kiosk_item = Kiosk.query.filter_by(card_id=card_id).first_or_404()
    set_code = kiosk_item.card.set_code
    db.session.delete(kiosk_item)
    db.session.commit()

    # Invalidate related caches
    current_app.redis_client.delete("kiosk:*")
    current_app.redis_client.delete("kiosk_sets:*")
    current_app.redis_client.delete(f"kiosk_set_cards:{set_code}:*")

    return '', 204

@kiosk_routes.route('/kiosk/stats', methods=['GET'])
def get_kiosk_stats():
    cache_key = "kiosk_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(func.sum(Kiosk.quantity_regular + Kiosk.quantity_foil)).scalar() or 0
        unique_cards = Kiosk.query.count()

        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * kiosk.quantity_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * kiosk.quantity_foil)
            )
            FROM kiosk
            JOIN cards ON cards.id = kiosk.card_id
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result)
        current_app.redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500