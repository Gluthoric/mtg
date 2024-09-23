import pandas as pd
from flask import Blueprint, jsonify, request
from models.collection import Collection
from models.card import Card
from models.kiosk import Kiosk
from models.set import Set
from database import db
from sqlalchemy.sql import func, asc, desc, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging

collection_routes = Blueprint('collection_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    try:
        diagnostic_info = {
            "set_count": Set.query.count(),
            "collection_count": Collection.query.count(),
            "card_count": Card.query.count(),
            "step1_count": 0,
            "step2_count": 0,
            "step3_count": 0,
            "total_count_before_pagination": 0
        }

        # Extract query parameters
        name = request.args.get('name', type=str, default='')
        set_type = request.args.get('set_type', type=str, default='')
        sort_by = request.args.get('sort_by', type=str, default='released_at')
        sort_order = request.args.get('sort_order', type=str, default='desc')
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=20)

        logger.info(f"Received parameters: name={name}, set_type={set_type}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Base query with specific columns and collection count using outer joins
        query = db.session.query(
            Set.id,
            Set.code,
            Set.name,
            Set.released_at,
            Set.set_type,
            Set.card_count,
            Set.digital,
            Set.foil_only,
            Set.icon_svg_uri,
            func.count(Collection.card_id).label('collection_count')
        ).outerjoin(Card, Card.set_code == Set.code
        ).outerjoin(Collection, Collection.card_id == Card.id
        ).group_by(
            Set.id,
            Set.code,
            Set.name,
            Set.released_at,
            Set.set_type,
            Set.card_count,
            Set.digital,
            Set.foil_only,
            Set.icon_svg_uri
        )

        # Step 1: After joining Set and Card
        diagnostic_info["step1_count"] = query.count()

        # Step 2: After joining with Collection
        diagnostic_info["step2_count"] = query.count()

        # Step 3: After grouping
        diagnostic_info["step3_count"] = query.count()

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.info(f"Applied filter: Set.name ilike '%{name}%'")
        if set_type:
            query = query.filter(Set.set_type == set_type)
            logger.info(f"Applied filter: Set.set_type == '{set_type}'")

        # Validate and apply sorting
        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(error_message)
            return jsonify({"error": error_message, "diagnostic_info": diagnostic_info}), 400

        if sort_by == 'collection_count':
            sort_column = func.count(Collection.card_id)
        else:
            sort_column = getattr(Set, sort_by)

        if sort_order.lower() == 'asc':
            query = query.order_by(asc(sort_column))
            logger.info(f"Sorting by {sort_by} in ascending order")
        else:
            query = query.order_by(desc(sort_column))
            logger.info(f"Sorting by {sort_by} in descending order")

        # Get total count before pagination
        total_count = query.count()
        diagnostic_info["total_count_before_pagination"] = total_count
        logger.info(f"Total count before pagination: {total_count}")

        # Apply pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

        # Build response
        sets_list = []
        for row in paginated_sets.items:
            set_data = {
                'id': row.id,
                'code': row.code,
                'name': row.name,
                'released_at': row.released_at,
                'set_type': row.set_type,
                'card_count': row.card_count,
                'digital': row.digital,
                'foil_only': row.foil_only,
                'icon_svg_uri': row.icon_svg_uri
            }
            collection_count = row.collection_count
            collection_percentage = (collection_count / row.card_count) * 100 if row.card_count else 0
            sets_list.append({
                **set_data,
                'collection_count': collection_count,
                'collection_percentage': collection_percentage
            })

        response = {
            'sets': sets_list,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page,
            'diagnostic_info': diagnostic_info
        }

        logger.info(f"Returning response with {len(sets_list)} sets")
        return jsonify(response), 200
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message, "diagnostic_info": diagnostic_info}), 500

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

    # Fetch the associated card
    card = Card.query.filter_by(id=card_id).first()
    if not card:
        return jsonify({"error": "Card not found."}), 404

    # Combine card data with updated quantities
    card_data = card.to_dict()
    card_data.update({
        'quantity_regular': collection_item.quantity_regular,
        'quantity_foil': collection_item.quantity_foil
    })

    return jsonify(card_data), 200

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
        logger.error(f"Failed to parse CSV: {str(e)}")
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 400

    required_columns = {
        'Name', 'Edition', 'Edition code', "Collector's number",
        'Price', 'Foil', 'Currency', 'Scryfall ID', 'Quantity'
    }
    if not required_columns.issubset(set(df.columns)):
        missing = required_columns - set(df.columns)
        return jsonify({"error": f"CSV is missing columns: {', '.join(missing)}"}), 400

    # **New Code Starts Here**
    # Replace blank 'Foil' values with False
    df['Foil'] = df['Foil'].fillna(False)          # Replace NaN with False
    df['Foil'] = df['Foil'].replace('', False)    # Replace empty strings with False
    # **New Code Ends Here**

    try:
        with db.session.begin_nested():
            for index, row in df.iterrows():
                try:
                    process_csv_row(row, index)
                except ValueError as e:
                    logger.error(f"Error processing row {index + 2}: {str(e)}")
                    # Optionally, collect errors to return after processing
                    continue  # Skip to the next row
                except IntegrityError as e:
                    logger.error(f"IntegrityError at row {index + 2}: {str(e)}")
                    db.session.rollback()
                    return jsonify({"error": f"Database integrity error at row {index + 2}: {str(e)}"}), 500

                # Flush every 100 rows to catch potential errors earlier
                if index % 100 == 0:
                    db.session.flush()

        db.session.commit()
        logger.info("CSV imported successfully")
        return jsonify({"message": "CSV imported successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during CSV import: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

def process_csv_row(row, index):
    scryfall_id = row['Scryfall ID']
    card_name = row['Name']

    # Validate and parse quantity
    try:
        quantity = int(row['Quantity'])
        if quantity < 1:
            raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")
    except ValueError:
        raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")

    # Normalize foil value
    foil = row['Foil']
    if isinstance(foil, bool):
        foil_status = foil
    else:
        # This should not happen as we've already replaced blanks with False
        raise ValueError(f"Foil value must be boolean for card '{card_name}' at row {index + 2}.")

    # Fetch the card from the database
    card = Card.query.filter_by(id=scryfall_id).first()
    if not card:
        raise ValueError(f"Card with Scryfall ID '{scryfall_id}' not found in the database.")

    # Fetch or create collection and kiosk entries
    collection_item = Collection.query.filter_by(card_id=card.id).first()
    kiosk_item = Kiosk.query.filter_by(card_id=card.id).first()

    if foil_status:
        handle_foil_card(card, quantity, collection_item, kiosk_item)
    else:
        handle_non_foil_card(card, quantity, collection_item, kiosk_item)

def handle_foil_card(card, quantity, collection_item, kiosk_item):
    if collection_item and collection_item.quantity_foil > 0:
        if kiosk_item:
            kiosk_item.quantity_foil += quantity
        else:
            kiosk_item = Kiosk(card_id=card.id, quantity_foil=quantity)
            db.session.add(kiosk_item)
    else:
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

def handle_non_foil_card(card, quantity, collection_item, kiosk_item):
    has_collection_copy = collection_item and (collection_item.quantity_regular > 0 or collection_item.quantity_foil > 0)

    if not has_collection_copy:
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
        if kiosk_item:
            kiosk_item.quantity_regular += quantity
        else:
            kiosk_item = Kiosk(card_id=card.id, quantity_regular=quantity)
            db.session.add(kiosk_item)
