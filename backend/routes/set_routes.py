from flask import Blueprint, jsonify, request
from models.set import Set
from models.card import Card
from database import db
from sqlalchemy import asc, desc
from sqlalchemy.orm import joinedload

set_routes = Blueprint('set_routes', __name__)

@set_routes.route('/sets', methods=['GET'])
def get_all_sets():
    try:
        # Extract query parameters
        name = request.args.get('name', type=str, default='')
        set_type = request.args.get('set_type', type=str, default='')
        sort_by = request.args.get('sort_by', type=str, default='released_at')
        sort_order = request.args.get('sort_order', type=str, default='desc')
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=20)

        query = Set.query

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
        if set_type:
            query = query.filter(Set.set_type == set_type)

        # Apply sorting
        if sort_order.lower() == 'asc':
            query = query.order_by(asc(getattr(Set, sort_by)))
        else:
            query = query.order_by(desc(getattr(Set, sort_by)))

        # Apply pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)

        sets = [set.to_dict() for set in paginated_sets.items]

        return jsonify({
            'sets': sets,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }), 200
    except AttributeError:
        return jsonify({"error": f"Invalid sort_by field: {sort_by}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@set_routes.route('/sets/<string:set_code>', methods=['GET'])
def get_set(set_code):
    set_instance = Set.query.filter_by(code=set_code).first_or_404()
    return jsonify(set_instance.to_dict()), 200

@set_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
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
    cards_data = []
    for card in cards:
        card_dict = {
            'id': card.id,
            'name': card.name,
            'rarity': card.rarity,
            'quantity_regular': card.quantity_collection_regular,
            'quantity_foil': card.quantity_collection_foil,
            'set_name': card.set.name if card.set else '',
            'set_code': card.set_code,
            'collector_number': card.collector_number,
            'mana_cost': card.mana_cost,
            'cmc': card.cmc,
            'type_line': card.type_line,
            'oracle_text': card.oracle_text,
            'colors': card.colors,
            'color_identity': card.color_identity,
            'keywords': card.keywords,
            'legalities': card.legalities,
            'reserved': card.reserved,
            'foil': card.foil,
            'nonfoil': card.nonfoil,
            'full_art': card.full_art,
            'textless': card.textless,
            'promo': card.promo,
            'reprint': card.reprint,
            'variation': card.variation,
            'artist': card.artist,
            'frame': card.frame,
            'border_color': card.border_color,
            'released_at': card.released_at,
            'prices': card.prices,
        }
        # Include image URIs
        if hasattr(card, 'image_uris') and card.image_uris:
            card_dict['image_uris'] = card.image_uris

        # Include related URIs
        if card.related_uris:
            card_dict['related_uris'] = card.related_uris

        # Include purchase URIs
        if card.purchase_uris:
            card_dict['purchase_uris'] = card.purchase_uris

        cards_data.append(card_dict)

    return jsonify({
        'cards': cards_data,
        'total': len(cards_data),
        'pages': 1,
        'current_page': 1
    }), 200
