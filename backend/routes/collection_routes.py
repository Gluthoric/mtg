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

@collection_routes.route('/collection/sets', methods=['GET'])
def get_collection_sets():
    collection_sets = db.session.query(
        Set,
        func.count(Collection.card_id).label('collection_count')
    ).join(Card, Card.set_code == Set.code
    ).join(Collection, Collection.card_id == Card.id
    ).group_by(Set).all()

    sets_list = []
    for set, collection_count in collection_sets:
        collection_percentage = (collection_count / set.card_count) * 100 if set.card_count else 0
        sets_list.append({
            **set.to_dict(),
            'collection_count': collection_count,
            'collection_percentage': collection_percentage
        })

    return jsonify({'sets': sets_list}), 200

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

@collection_routes.route('/collection/sets/<string:set_code>/cards', methods=['GET'])
def get_collection_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name = request.args.get('name', '', type=str)
    rarity = request.args.get('rarity', '', type=str)

    query = Collection.query.join(Card).join(Set).filter(Set.code == set_code)

    if name:
        query = query.filter(Card.name.ilike(f'%{name}%'))
    if rarity:
        query = query.filter(Card.rarity == rarity)

    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [
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

    # Define required columns based on the new CSV format
    required_columns = {
        'Name',
        'Edition',
        'Edition code',
        "Collector's number",
        'Price',
        'Foil',
        'Currency',
        'Scryfall ID',
        'Quantity'
    }
    if not required_columns.issubset(set(df.columns)):
        missing = required_columns - set(df.columns)
        return jsonify({"error": f"CSV is missing columns: {', '.join(missing)}"}), 400

    # Process each row
    for index, row in df.iterrows():
        scryfall_id = row['Scryfall ID']
        card_name = row['Name']
        try:
            quantity = int(row['Quantity'])
            if quantity < 1:
                raise ValueError
        except ValueError:
            return jsonify({"error": f"Invalid quantity for card '{card_name}' at row {index + 2}."}), 400

        foil_status = str(row['Foil']).strip().lower()
        if foil_status in ['true', '1', 'yes', 'foil']:
            foil = True
        elif foil_status in ['false', '0', 'no', 'non-foil']:
            foil = False
        else:
            return jsonify({"error": f"Invalid foil value for card '{card_name}' at row {index + 2}."}), 400

        # Fetch the card by Scryfall ID
        card = Card.query.filter_by(id=scryfall_id).first()
        if not card:
            return jsonify({"error": f"Card with Scryfall ID '{scryfall_id}' not found in the database."}), 404

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
                # Collection does not have foil, add 1 foil to collection and the rest to kiosk
                to_collection = 1 if quantity >= 1 else 0
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
            # Handle non-foil cards
            has_collection_copy = False
            if collection_item:
                has_collection_copy = collection_item.quantity_regular > 0 or collection_item.quantity_foil > 0

            if not has_collection_copy:
                # Add 1 non-foil to collection, rest to kiosk
                to_collection = 1 if quantity >= 1 else 0
                to_kiosk = quantity - to_collection

                if to_collection > 0:
                    if collection_item:
                        collection_item.quantity_regular += to_collection
                    else:
                        collection_item = Collection(card_id=card.id, quantity_regular=to_collection)
                        db.session.add(collection_item)

                if to_kiosk > 0:
                    if kiosk_item:
                        kiosk_item.quantity_regular += to_kiosk
                    else:
                        kiosk_item = Kiosk(card_id=card.id, quantity_regular=to_kiosk)
                        db.session.add(kiosk_item)
            else:
                # Collection already has a copy, send all to kiosk
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