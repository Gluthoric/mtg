from flask import Blueprint, jsonify, request
from models.set import Set
from models.card import Card
from database import db
from sqlalchemy import asc, desc

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
    set = Set.query.filter_by(code=set_code).first_or_404()
    return jsonify(set.to_dict()), 200

@set_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name = request.args.get('name', '', type=str)
    rarity = request.args.get('rarity', '', type=str)

    query = Card.query.filter_by(set_code=set_code)

    if name:
        query = query.filter(Card.name.ilike(f'%{name}%'))
    if rarity:
        query = query.filter(Card.rarity == rarity)

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': cards.page
    }), 200