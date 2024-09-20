from flask import Blueprint, jsonify, request
from models.collection import Collection
from models.card import Card
from database import db

collection_routes = Blueprint('collection_routes', __name__)

@collection_routes.route('/collection', methods=['GET'])
def get_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    collection = Collection.query.join(Card).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'collection': [
            {**item.card.to_dict(), 'quantity': item.to_dict()}
            for item in collection.items
        ],
        'total': collection.total,
        'pages': collection.pages,
        'current_page': page
    }), 200

@collection_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    collection_item = Collection.query.filter_by(card_id=card_id).first()

    if collection_item:
        collection_item.quantity_regular = quantity_regular
        collection_item.quantity_foil = quantity_foil
    else:
        collection_item = Collection(card_id=card_id, quantity_regular=quantity_regular, quantity_foil=quantity_foil)
        db.session.add(collection_item)

    db.session.commit()

    return jsonify(collection_item.to_dict()), 200

@collection_routes.route('/collection/<string:card_id>', methods=['DELETE'])
def remove_from_collection(card_id):
    collection_item = Collection.query.filter_by(card_id=card_id).first_or_404()
    db.session.delete(collection_item)
    db.session.commit()

    return '', 204

@collection_routes.route('/collection/stats', methods=['GET'])
def get_collection_stats():
    total_cards = db.session.query(db.func.sum(Collection.quantity_regular + Collection.quantity_foil)).scalar() or 0
    unique_cards = Collection.query.count()
    total_value = db.session.query(
        db.func.sum(
            db.cast(db.func.json_extract(Card.prices, '$.usd'), db.Float) * Collection.quantity_regular +
            db.cast(db.func.json_extract(Card.prices, '$.usd_foil'), db.Float) * Collection.quantity_foil
        )
    ).join(Card).scalar() or 0

    return jsonify({
        'total_cards': total_cards,
        'unique_cards': unique_cards,
        'total_value': round(total_value, 2)
    }), 200