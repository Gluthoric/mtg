from flask import Blueprint, jsonify, request
from models.kiosk import Kiosk
from models.card import Card
from database import db

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
    total_cards = db.session.query(db.func.sum(Kiosk.quantity_regular + Kiosk.quantity_foil)).scalar() or 0
    unique_cards = Kiosk.query.count()
    total_value = db.session.query(
        db.func.sum(
            db.cast(db.func.json_extract(Card.prices, '$.usd'), db.Float) * Kiosk.quantity_regular +
            db.cast(db.func.json_extract(Card.prices, '$.usd_foil'), db.Float) * Kiosk.quantity_foil
        )
    ).join(Card).scalar() or 0

    return jsonify({
        'total_cards': total_cards,
        'unique_cards': unique_cards,
        'total_value': round(total_value, 2)
    }), 200