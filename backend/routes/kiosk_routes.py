from flask import Blueprint, jsonify, request
from models.kiosk import Kiosk
from models.card import Card
from models.set import Set
from database import db
from sqlalchemy.sql import func, text
from sqlalchemy import distinct

kiosk_routes = Blueprint('kiosk_routes', __name__)

@kiosk_routes.route('/kiosk', methods=['GET'])
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    kiosk = Kiosk.query.join(Card).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'kiosk': [
            {**item.card.to_dict(), 'quantity': item.to_dict()}
            for item in kiosk.items
        ],
        'total': kiosk.total,
        'pages': kiosk.pages,
        'current_page': page
    }), 200

@kiosk_routes.route('/kiosk/sets', methods=['GET'])
def get_kiosk_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # Query to get sets with cards in the kiosk
    kiosk_sets = db.session.query(Set).\
        join(Card, Card.set_code == Set.code).\
        join(Kiosk, Kiosk.card_id == Card.id).\
        filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0)).\
        distinct()

    # Apply sorting
    sort_by = request.args.get('sortBy', 'released_at')
    sort_order = request.args.get('sortOrder', 'desc')

    if sort_order == 'desc':
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by).desc())
    else:
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by))

    # Paginate the results
    paginated_sets = kiosk_sets.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare the response
    sets_data = []
    for set_obj in paginated_sets.items:
        set_dict = set_obj.to_dict()

        # Count cards in kiosk for this set
        kiosk_count = db.session.query(func.count(distinct(Card.id))).\
            join(Kiosk, Kiosk.card_id == Card.id).\
            filter(Card.set_code == set_obj.code).\
            filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0)).\
            scalar()

        set_dict['kiosk_count'] = kiosk_count
        set_dict['kiosk_percentage'] = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

        sets_data.append(set_dict)

    return jsonify({
        'sets': sets_data,
        'total': paginated_sets.total,
        'pages': paginated_sets.pages,
        'current_page': page
    }), 200

@kiosk_routes.route('/kiosk/sets/<string:set_code>/cards', methods=['GET'])
def get_kiosk_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name_filter = request.args.get('name', '')
    rarity_filter = request.args.get('rarity', '')
    sort_by = request.args.get('sortBy', 'name')
    sort_order = request.args.get('sortOrder', 'asc')

    # Query to get cards in the kiosk for the specified set
    query = db.session.query(Card, Kiosk).\
        join(Kiosk, Kiosk.card_id == Card.id).\
        filter(Card.set_code == set_code).\
        filter((Kiosk.quantity_regular > 0) | (Kiosk.quantity_foil > 0))

    # Apply filters
    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))
    if rarity_filter:
        query = query.filter(Card.rarity == rarity_filter)

    # Apply sorting
    if sort_order == 'desc':
        query = query.order_by(getattr(Card, sort_by).desc())
    else:
        query = query.order_by(getattr(Card, sort_by))

    # Paginate the results
    paginated_cards = query.paginate(page=page, per_page=per_page, error_out=False)

    # Prepare the response
    cards_data = []
    for card, kiosk_item in paginated_cards.items:
        card_dict = card.to_dict()
        card_dict['quantity'] = kiosk_item.to_dict()
        cards_data.append(card_dict)

    # Get the set name
    set_name = Set.query.filter_by(code=set_code).first().name

    return jsonify({
        'cards': cards_data,
        'set_name': set_name,
        'total': paginated_cards.total,
        'pages': paginated_cards.pages,
        'current_page': page
    }), 200

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

    return jsonify(kiosk_item.to_dict()), 200

@kiosk_routes.route('/kiosk/<string:card_id>', methods=['DELETE'])
def remove_from_kiosk(card_id):
    kiosk_item = Kiosk.query.filter_by(card_id=card_id).first_or_404()
    db.session.delete(kiosk_item)
    db.session.commit()

    return '', 204

@kiosk_routes.route('/kiosk/stats', methods=['GET'])
def get_kiosk_stats():
    try:
        total_cards = db.session.query(func.sum(Kiosk.quantity_regular + Kiosk.quantity_foil)).scalar() or 0
        unique_cards = Kiosk.query.count()

        # Use a raw SQL query to calculate the total value
        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * kiosk.quantity_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * kiosk.quantity_foil)
            )
            FROM kiosk
            JOIN cards ON cards.id = kiosk.card_id
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        return jsonify({
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500