from flask import Blueprint, jsonify, request
from models.card import Card
from database import db
from sqlalchemy import or_

card_routes = Blueprint('card_routes', __name__)

@card_routes.route('/cards', methods=['GET'])
def get_cards():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
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
        query = query.filter(or_(*[Card.colors.contains([color]) for color in colors]))

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200

@card_routes.route('/cards/<string:card_id>', methods=['GET'])
def get_card(card_id):
    card = Card.query.get_or_404(card_id)
    return jsonify(card.to_dict()), 200

@card_routes.route('/cards/search', methods=['GET'])
def search_cards():
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cards = Card.query.filter(
        or_(
            Card.name.ilike(f'%{query}%'),
            Card.type_line.ilike(f'%{query}%'),
            Card.oracle_text.ilike(f'%{query}%')
        )
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200