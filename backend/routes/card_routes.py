import pandas as pd
import logging
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.orm import joinedload, load_only
from sqlalchemy.sql import func, asc, desc, text
from sqlalchemy import or_, distinct
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.card import Card
from models.set import Set
from database import db
import orjson

card_routes = Blueprint('card_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def serialize_cards(cards, quantity_type='collection'):
    if quantity_type == 'collection':
        return [{
            **card.to_dict(),
            'quantity_regular': card.quantity_collection_regular,
            'quantity_foil': card.quantity_collection_foil
        } for card in cards]
    elif quantity_type == 'kiosk':
        return [{
            **card.to_dict(),
            'quantity_regular': card.quantity_kiosk_regular,
            'quantity_foil': card.quantity_kiosk_foil
        } for card in cards]
    else:
        return [card.to_dict() for card in cards]

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
        query = query.filter(or_(*[Card.colors.contains([color.strip()]) for color in colors]))

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
    query_param = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cards = Card.query.filter(
        or_(
            Card.name.ilike(f'%{query_param}%'),
            Card.type_line.ilike(f'%{query_param}%'),
            Card.oracle_text.ilike(f'%{query_param}%')
        )
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'cards': [card.to_dict() for card in cards.items],
        'total': cards.total,
        'pages': cards.pages,
        'current_page': page
    }), 200

# Collection Routes

@card_routes.route('/collection', methods=['GET'])
def get_collection():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    set_code = request.args.get('set_code', '', type=str)

    cache_key = f"collection:page:{page}:per_page:{per_page}:set_code:{set_code}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    query = Card.query

    if set_code:
        query = query.filter(Card.set_code == set_code)

    query = query.filter((Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0))

    collection = query.paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'collection': serialize_cards(collection.items, quantity_type='collection'),
        'total': collection.total,
        'pages': collection.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/collection/sets', methods=['GET'])
def get_collection_sets():
    try:
        name = request.args.get('name', type=str)
        set_type = request.args.get('set_type', type=str)
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        cache_key = f"collection_sets:name:{name}:set_type:{set_type}:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
        cached_data = current_app.redis_client.get(cache_key)

        if cached_data:
            return current_app.response_class(
                response=cached_data,
                status=200,
                mimetype='application/json'
            )

        logger.info(f"Received parameters: name={name}, set_type={set_type}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Subquery to calculate collection_count per set_code
        subquery = db.session.query(
            Card.set_code.label('set_code'),
            func.sum(Card.quantity_collection_regular + Card.quantity_collection_foil).label('collection_count')
        ).group_by(Card.set_code).subquery()

        # Main query to fetch sets with their collection counts
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
            func.coalesce(subquery.c.collection_count, 0).label('collection_count')
        ).outerjoin(subquery, Set.code == subquery.c.set_code)

        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.info(f"Applied filter: Set.name ilike '%{name}%'")
        if set_type:
            query = query.filter(Set.set_type == set_type)
            logger.info(f"Applied filter: Set.set_type == '{set_type}'")

        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(error_message)
            return jsonify({"error": error_message}), 400

        if sort_by == 'collection_count':
            sort_column = subquery.c.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        if sort_order.lower() == 'asc':
            query = query.order_by(asc(sort_column))
            logger.info(f"Sorting by {sort_by} in ascending order")
        else:
            query = query.order_by(desc(sort_column))
            logger.info(f"Sorting by {sort_by} in descending order")

        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

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
            'current_page': paginated_sets.page
        }

        serialized_data = orjson.dumps(response)
        current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

        logger.info(f"Returning response with {len(sets_list)} sets")
        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

@card_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    card.quantity_collection_regular = quantity_regular
    card.quantity_collection_foil = quantity_foil

    db.session.commit()

    # Invalidate related caches
    current_app.redis_client.delete("collection:*")
    current_app.redis_client.delete("collection_sets:*")
    current_app.redis_client.delete("collection_stats")

    card_data = card.to_dict()
    card_data.update({
        'quantity_regular': card.quantity_collection_regular,
        'quantity_foil': card.quantity_collection_foil
    })

    return current_app.response_class(
        response=orjson.dumps(card_data),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/collection/stats', methods=['GET'])
def get_collection_stats():
    cache_key = "collection_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(func.sum(Card.quantity_collection_regular + Card.quantity_collection_foil)).scalar() or 0
        unique_cards = Card.query.filter((Card.quantity_collection_regular > 0) | (Card.quantity_collection_foil > 0)).count()

        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_collection_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_collection_foil)
            )
            FROM cards
            WHERE quantity_collection_regular > 0 OR quantity_collection_foil > 0
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result)
        current_app.redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@card_routes.route('/collection/sets/<string:set_code>/cards', methods=['GET'])
def get_collection_set_cards(set_code):
    name = request.args.get('name', '', type=str)
    rarity = request.args.get('rarity', '', type=str)
    colors = request.args.getlist('colors') + request.args.getlist('colors[]')

    try:
        # Build the query with only required columns using model attributes
        query = Card.query.options(
            load_only(
                Card.id,
                Card.name,
                Card.image_uris,
                Card.collector_number,
                Card.prices,
                Card.rarity,
                Card.set_name,
                Card.quantity_collection_regular,
                Card.quantity_collection_foil
            )
        ).filter(Card.set_code == set_code)

        # Apply filters
        if name:
            query = query.filter(Card.name.ilike(f'%{name}%'))
        if rarity:
            query = query.filter(Card.rarity == rarity)
        if colors:
            VALID_COLORS = {'W', 'U', 'B', 'R', 'G'}
            invalid_colors = set(colors) - VALID_COLORS
            if invalid_colors:
                return jsonify({"error": f"Invalid colors: {', '.join(invalid_colors)}"}), 400

            # Use JSONB array contains operator '?|'
            colors_str = "{" + ",".join(f'"{c}"' for c in colors) + "}"
            query = query.filter(text("cards.colors ?| :colors_str").bindparams(colors_str=colors_str))

        # Execute the query
        cards = query.all()

        # Prepare the response
        result = {
            'cards': [{
                'id': card.id,
                'name': card.name,
                'image_uris': card.image_uris,
                'collector_number': card.collector_number,
                'prices': card.prices,
                'rarity': card.rarity,
                'set_name': card.set_name,
                'quantity_regular': card.quantity_collection_regular,
                'quantity_foil': card.quantity_collection_foil
            } for card in cards],
            'total': len(cards),
        }

        return jsonify(result), 200
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

@card_routes.route('/collection/import_csv', methods=['POST'])
def import_collection_csv():
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

    df['Foil'] = df['Foil'].fillna(False).replace('', False)

    try:
        with db.session.begin_nested():
            for index, row in df.iterrows():
                try:
                    process_collection_csv_row(row, index)
                except ValueError as e:
                    logger.error(f"Error processing row {index + 2}: {str(e)}")
                    continue
                except IntegrityError as e:
                    logger.error(f"IntegrityError at row {index + 2}: {str(e)}")
                    db.session.rollback()
                    return jsonify({"error": f"Database integrity error at row {index + 2}: {str(e)}"}), 500

                if index % 100 == 0:
                    db.session.flush()

        db.session.commit()
        logger.info("CSV imported successfully")

        # Invalidate related caches
        current_app.redis_client.delete("collection:*")
        current_app.redis_client.delete("collection_sets:*")
        current_app.redis_client.delete("collection_stats")

        return jsonify({"message": "CSV imported successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during CSV import: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

def process_collection_csv_row(row, index):
    scryfall_id = row['Scryfall ID']
    card_name = row['Name']

    try:
        quantity = int(row['Quantity'])
        if quantity < 1:
            raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")
    except ValueError:
        raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")

    foil = row['Foil']
    if isinstance(foil, bool):
        foil_status = foil
    else:
        raise ValueError(f"Foil value must be boolean for card '{card_name}' at row {index + 2}.")

    card = Card.query.filter_by(id=scryfall_id).first()
    if not card:
        raise ValueError(f"Card with Scryfall ID '{scryfall_id}' not found in the database.")

    if foil_status:
        card.quantity_collection_foil += quantity
    else:
        card.quantity_collection_regular += quantity

    db.session.add(card)

# Kiosk Routes

@card_routes.route('/kiosk', methods=['GET'])
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cache_key = f"kiosk:page:{page}:per_page:{per_page}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    kiosk = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).paginate(page=page, per_page=per_page, error_out=False)

    result = {
        'kiosk': serialize_cards(kiosk.items, quantity_type='kiosk'),
        'total': kiosk.total,
        'pages': kiosk.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/sets', methods=['GET'])
def get_kiosk_sets():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sortBy', 'released_at')
    sort_order = request.args.get('sortOrder', 'desc')

    cache_key = f"kiosk_sets:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    kiosk_sets = db.session.query(Set).\
        join(Card, Card.set_code == Set.code).\
        filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
        distinct()

    if sort_order == 'desc':
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by).desc())
    else:
        kiosk_sets = kiosk_sets.order_by(getattr(Set, sort_by))

    paginated_sets = kiosk_sets.paginate(page=page, per_page=per_page, error_out=False)

    sets_data = []
    for set_obj in paginated_sets.items:
        set_dict = set_obj.to_dict()

        kiosk_count = db.session.query(func.count(distinct(Card.id))).\
            filter(Card.set_code == set_obj.code).\
            filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
            scalar()

        set_dict['kiosk_count'] = kiosk_count
        set_dict['kiosk_percentage'] = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

        sets_data.append(set_dict)

    result = {
        'sets': sets_data,
        'total': paginated_sets.total,
        'pages': paginated_sets.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 600, serialized_data)  # Cache for 10 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/sets/<string:set_code>/cards', methods=['GET'])
def get_kiosk_set_cards(set_code):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    name_filter = request.args.get('name', '')
    rarity_filter = request.args.get('rarity', '')
    sort_by = request.args.get('sortBy', 'name')
    sort_order = request.args.get('sortOrder', 'asc')

    cache_key = f"kiosk_set_cards:{set_code}:page:{page}:per_page:{per_page}:name:{name_filter}:rarity:{rarity_filter}:sort_by:{sort_by}:sort_order:{sort_order}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    query = Card.query.filter(Card.set_code == set_code).filter(
        (Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)
    )

    if name_filter:
        query = query.filter(Card.name.ilike(f'%{name_filter}%'))
    if rarity_filter:
        query = query.filter(Card.rarity == rarity_filter)

    if sort_order == 'desc':
        query = query.order_by(getattr(Card, sort_by).desc())
    else:
        query = query.order_by(getattr(Card, sort_by))

    paginated_cards = query.paginate(page=page, per_page=per_page, error_out=False)

    cards_data = serialize_cards(paginated_cards.items, quantity_type='kiosk')

    set_instance = Set.query.filter_by(code=set_code).first()
    set_name = set_instance.name if set_instance else ''

    result = {
        'cards': cards_data,
        'set_name': set_name,
        'total': paginated_cards.total,
        'pages': paginated_cards.pages,
        'current_page': page
    }

    serialized_data = orjson.dumps(result)
    current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/<string:card_id>', methods=['POST', 'PUT'])
def update_kiosk(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    card.quantity_kiosk_regular = quantity_regular
    card.quantity_kiosk_foil = quantity_foil

    db.session.commit()

    # Invalidate related caches
    current_app.redis_client.delete("kiosk:*")
    current_app.redis_client.delete("kiosk_sets:*")
    current_app.redis_client.delete(f"kiosk_set_cards:{card.set_code}:*")

    # Serialize and return updated card
    card_data = card.to_dict()
    card_data.update({
        'quantity_regular': card.quantity_kiosk_regular,
        'quantity_foil': card.quantity_kiosk_foil
    })

    return current_app.response_class(
        response=orjson.dumps(card_data),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/stats', methods=['GET'])
def get_kiosk_stats():
    cache_key = "kiosk_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data,
            status=200,
            mimetype='application/json'
        )

    try:
        total_cards = db.session.query(func.sum(Card.quantity_kiosk_regular + Card.quantity_kiosk_foil)).scalar() or 0
        unique_cards = Card.query.filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).count()

        total_value_query = text("""
            SELECT SUM(
                (CAST(COALESCE(NULLIF((prices::json->>'usd'), ''), '0') AS FLOAT) * quantity_kiosk_regular) +
                (CAST(COALESCE(NULLIF((prices::json->>'usd_foil'), ''), '0') AS FLOAT) * quantity_kiosk_foil)
            )
            FROM cards
            WHERE quantity_kiosk_regular > 0 OR quantity_kiosk_foil > 0
        """)
        total_value = db.session.execute(total_value_query).scalar() or 0

        result = {
            'total_cards': int(total_cards),
            'unique_cards': unique_cards,
            'total_value': round(total_value, 2)
        }

        serialized_data = orjson.dumps(result)
        current_app.redis_client.setex(cache_key, 3600, serialized_data)  # Cache for 1 hour

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@card_routes.route('/kiosk/import_csv', methods=['POST'])
def import_kiosk_csv():
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

    df['Foil'] = df['Foil'].fillna(False).replace('', False)

    try:
        with db.session.begin_nested():
            for index, row in df.iterrows():
                try:
                    process_kiosk_csv_row(row, index)
                except ValueError as e:
                    logger.error(f"Error processing row {index + 2}: {str(e)}")
                    continue
                except IntegrityError as e:
                    logger.error(f"IntegrityError at row {index + 2}: {str(e)}")
                    db.session.rollback()
                    return jsonify({"error": f"Database integrity error at row {index + 2}: {str(e)}"}), 500

                if index % 100 == 0:
                    db.session.flush()

        db.session.commit()
        logger.info("CSV imported successfully")

        # Invalidate related caches
        current_app.redis_client.delete("kiosk:*")
        current_app.redis_client.delete("kiosk_sets:*")
        current_app.redis_client.delete("kiosk_stats")

        return jsonify({"message": "CSV imported successfully"}), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error during CSV import: {str(e)}")
        return jsonify({"error": f"Database error: {str(e)}"}), 500

def process_kiosk_csv_row(row, index):
    scryfall_id = row['Scryfall ID']
    card_name = row['Name']

    try:
        quantity = int(row['Quantity'])
        if quantity < 1:
            raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")
    except ValueError:
        raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")

    foil = row['Foil']
    if isinstance(foil, bool):
        foil_status = foil
    else:
        raise ValueError(f"Foil value must be boolean for card '{card_name}' at row {index + 2}.")

    card = Card.query.filter_by(id=scryfall_id).first()
    if not card:
        raise ValueError(f"Card with Scryfall ID '{scryfall_id}' not found in the database.")

    if foil_status:
        card.quantity_kiosk_foil += quantity
    else:
        card.quantity_kiosk_regular += quantity

    db.session.add(card)
