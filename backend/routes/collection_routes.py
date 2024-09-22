import pandas as pd
from flask import Blueprint, jsonify, request
from models.collection import Collection
from models.card import Card
from models.kiosk import Kiosk
from models.set import Set
from database import db
from sqlalchemy.sql import func, text
from sqlalchemy.exc import SQLAlchemyError

collection_routes = Blueprint('collection_routes', __name__)

@collection_routes.route('/collection', methods=['GET'])
def get_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    set_code = request.args.get('set_code', '', type=str)

    query = Collection.query.join(Card).join(Set)

    if set_code:
        query = query.filter(Set.code == set_code)

    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'collection': [
            {
                **item.card.to_dict(),
                'quantity_regular': item.quantity_regular,
                'quantity_foil': item.quantity_foil
            }
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
    try:
        total_cards = db.session.query(func.sum(Collection.quantity_regular + Collection.quantity_foil)).scalar() or 0
        unique_cards = Collection.query.count()

        # Use a raw SQL query to calculate the total value
        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * collections.quantity_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * collections.quantity_foil)
            )
            FROM collections
            JOIN cards ON cards.id = collections.card_id
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        return jsonify({
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@collection_routes.route('/collection/import_csv', methods=['POST'])
def import_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Only CSV files are allowed"}), 400

    try:
        df = pd.read_csv(file)
    except Exception as e:
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 400

    # Expected CSV Columns: card_name, quantity, foil (boolean)
    required_columns = {'card_name', 'quantity', 'foil'}
    if not required_columns.issubset(set(df.columns)):
        return jsonify({"error": f"CSV must contain columns: {', '.join(required_columns)}"}), 400

    # Process each row
    for index, row in df.iterrows():
        card_name = row['card_name']
        quantity = int(row['quantity'])
        foil = bool(row['foil'])

        # Fetch the card by name
        card = Card.query.filter_by(name=card_name).first()
        if not card:
            return jsonify({"error": f"Card '{card_name}' not found in the database."}), 404

        # Fetch existing collection and kiosk items
        collection_item = Collection.query.filter_by(card_id=card.id).first()
        kiosk_item = Kiosk.query.filter_by(card_id=card.id).first()

        if foil:
            # Handle foil cards
            if collection_item and collection_item.quantity_foil > 0:
                # Collection already has foil, send all to kiosk
                if kiosk_item:
                    kiosk_item.quantity_foil += quantity
                else:
                    kiosk_item = Kiosk(card_id=card.id, quantity_foil=quantity)
                    db.session.add(kiosk_item)
            else:
                # Send 1 foil to collection, rest to kiosk
                to_collection = min(1, quantity)
                to_kiosk = quantity - to_collection

                if to_collection > 0:
                    if collection_item:
                        collection_item.quantity_foil += to_collection
                    else:
                        collection_item = Collection(card_id=card.id, quantity_foil=to_collection)
                        db.session.add(collection_item)

                if to_kiosk > 0:
                    if kiosk_item:
                        kiosk_item.quantity_foil += to_kiosk
                    else:
                        kiosk_item = Kiosk(card_id=card.id, quantity_foil=to_kiosk)
                        db.session.add(kiosk_item)
        else:
            # Handle non-foil cards: all go to kiosk
            if kiosk_item:
                kiosk_item.quantity_regular += quantity
            else:
                kiosk_item = Kiosk(card_id=card.id, quantity_regular=quantity)
                db.session.add(kiosk_item)

    try:
        db.session.commit()
        return jsonify({"message": "CSV imported successfully"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": f"Database error: {str(e)}"}), 500

# Add other collection routes here