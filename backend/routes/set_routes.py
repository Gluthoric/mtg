from flask import Blueprint, jsonify, request
from models.set import Set
from models.card import Card
from database import db

set_routes = Blueprint('set_routes', __name__)

@set_routes.route('/sets', methods=['GET'])
def get_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    set_type = request.args.get('set_type', '')

    query = Set.query

    if set_type:
        query = query.filter(Set.set_type == set_type)

    sets = query.order_by(Set.released_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'sets': [s.to_dict() for s in sets.items],
        'total': sets.total,
        'pages': sets.pages,
        'current_page': page
    }), 200

@set_routes.route('/sets/<string:set_code>', methods=['GET'])
def get_set(set_code):
    set = Set.query.filter_by(code=set_code).first_or_404()
    return jsonify(set.to_dict()), 200

@set_routes.route('/sets/<string:set_code>/cards', methods=['GET'])
def get_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cards = Card.query.filter_by(set_code=set_code).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200