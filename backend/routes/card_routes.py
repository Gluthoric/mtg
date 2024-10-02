import pandas as pd
import logging
from flask import Blueprint, jsonify, request, current_app
import time
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import joinedload, load_only, subqueryload, aliased
from sqlalchemy import func, case, or_, distinct, Float
from sqlalchemy.sql import func, asc, desc, text
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.card import Card
from models.set import Set
from models.set_collection_count import SetCollectionCount
from database import db
import orjson
from decimal import Decimal
from utils.categorization import get_card_category_case, get_category_case

card_routes = Blueprint('card_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def monitor_cache(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()

        # Increment total calls
        current_app.redis_client.incr('cache_total_calls')

        # Increment hits or misses
        if result is not None:
            current_app.redis_client.incr('cache_hits')
        else:
            current_app.redis_client.incr('cache_misses')

        # Record response time
        current_app.redis_client.lpush('cache_response_times', end_time - start_time)
        current_app.redis_client.ltrim('cache_response_times', 0, 999)  # Keep last 1000 response times

        return result
    return wrapper

def convert_decimals(obj):
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

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
    per_page = request.args.get('per_page', 50, type=int)
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
    card = Card.query.options(load_only(
        Card.id, Card.name, Card.set_name, Card.set_code, Card.collector_number,
        Card.type_line, Card.rarity, Card.mana_cost, Card.cmc, Card.oracle_text,
        Card.colors, Card.image_uris, Card.prices, Card.quantity_collection_regular,
        Card.quantity_collection_foil, Card.quantity_kiosk_regular, Card.quantity_kiosk_foil,
        Card.frame_effects, Card.promo_types, Card.promo, Card.reprint, Card.variation,
        Card.oversized, Card.keywords
    )).get_or_404(card_id)
    return jsonify(card.to_dict()), 200

@card_routes.route('/cards/search', methods=['GET'])
def search_cards():
    query_param = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    query = Card.query.options(load_only(
        Card.id, Card.name, Card.set_name, Card.set_code, Card.collector_number,
        Card.type_line, Card.rarity, Card.mana_cost, Card.cmc, Card.oracle_text,
        Card.colors, Card.image_uris, Card.prices, Card.quantity_collection_regular,
        Card.quantity_collection_foil, Card.quantity_kiosk_regular, Card.quantity_kiosk_foil,
        Card.frame_effects, Card.promo_types, Card.promo, Card.reprint, Card.variation,
        Card.oversized, Card.keywords
    )).filter(
        or_(
            Card.name.ilike(f'%{query_param}%'),
            Card.type_line.ilike(f'%{query_param}%'),
            Card.oracle_text.ilike(f'%{query_param}%')
        )
    )

    cards = query.paginate(page=page, per_page=per_page, error_out=False)

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
    per_page = request.args.get('per_page', 50, type=int)
    set_code = request.args.get('set_code', '', type=str)

    cache_key = f"collection:page:{page}:per_page:{per_page}:set_code:{set_code}"

    @monitor_cache
    def get_cached_data(key):
        return current_app.redis_client.get(key)

    cached_data = get_cached_data(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
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

    serialized_data = orjson.dumps(result).decode()

    # Dynamically set cache expiration based on data size
    cache_expiration = min(300, max(60, len(serialized_data) // 1000))  # Between 1-5 minutes based on size
    current_app.redis_client.setex(cache_key, cache_expiration, serialized_data)

    return current_app.response_class(
        response=serialized_data,
        status=200,
        mimetype='application/json'
    )


from collections import defaultdict

from collections import defaultdict
from sqlalchemy import func, cast, Float
from sqlalchemy.orm import joinedload, subqueryload
from sqlalchemy.sql import asc, desc

@card_routes.route('/collection/sets', methods=['GET'])
def get_collection_sets():
    try:
        # Extract query parameters
        name = request.args.get('name', type=str)
        set_types = request.args.getlist('set_type[]')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        sort_by = request.args.get('sort_by', 'released_at', type=str)
        sort_order = request.args.get('sort_order', 'desc', type=str)

        # Log received parameters
        logger.info(f"get_collection_sets: Received parameters: name={name}, set_types={set_types}, sort_by={sort_by}, sort_order={sort_order}, page={page}, per_page={per_page}")

        # Construct cache key
        cache_key = f"collection_sets:name:{name}:set_type:{','.join(set_types)}:page:{page}:per_page:{per_page}:sort_by:{sort_by}:sort_order:{sort_order}"
        cached_data = current_app.redis_client.get(cache_key)

        if cached_data:
            logger.info("get_collection_sets: Returning cached data")
            return current_app.response_class(
                response=cached_data.decode(),
                status=200,
                mimetype='application/json'
            )

        logger.info("get_collection_sets: Cache miss, fetching data from database")

        # Define valid sort fields and prevent SQL injection
        valid_sort_fields = {'released_at', 'name', 'collection_count', 'card_count'}
        if sort_by not in valid_sort_fields:
            error_message = f"Invalid sort_by field: {sort_by}"
            logger.error(f"get_collection_sets: {error_message}")
            return jsonify({"error": error_message}), 400

        # Determine sort column
        if sort_by == 'collection_count':
            sort_column = SetCollectionCount.collection_count
        else:
            sort_column = getattr(Set, sort_by)

        # Apply sort order
        order_func = desc if sort_order.lower() == 'desc' else asc

        # Build a query that fetches the sets and aggregates the total card values and collection counts
        subquery = (
            db.session.query(
                Card.set_code,
                func.sum(
                    (func.cast((Card.prices['usd'].astext), Float) * Card.quantity_collection_regular) +
                    (func.cast((Card.prices['usd_foil'].astext), Float) * Card.quantity_collection_foil)
                ).label('total_value')
            )
            .group_by(Card.set_code)
            .subquery()
        )

        query = db.session.query(
            Set,
            SetCollectionCount.collection_count,
            subquery.c.total_value
        ).outerjoin(
            SetCollectionCount, Set.code == SetCollectionCount.set_code
        ).outerjoin(
            subquery, Set.code == subquery.c.set_code
        )

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
            logger.debug(f"get_collection_sets: Applied filter: Set.name ilike '%{name}%'")
        if set_types:
            query = query.filter(Set.set_type.in_(set_types))
            logger.debug(f"get_collection_sets: Applied filter: Set.set_type IN {set_types}")
        else:
            # Use the partial index for relevant set types if no specific set_types are provided
            default_set_types = ['core', 'expansion', 'masters', 'draft_innovation', 'funny', 'commander']
            query = query.filter(Set.set_type.in_(default_set_types))
            logger.debug("get_collection_sets: Applied filter: Using partial index for relevant set types")

        # Apply sorting
        query = query.order_by(order_func(sort_column))

        # Execute the query with pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)
        logger.info(f"get_collection_sets: Paginated sets: page={paginated_sets.page}, pages={paginated_sets.pages}, total={paginated_sets.total}")

        # Process results
        sets_list = []
        for set_instance, collection_count, total_value in paginated_sets.items:
            set_data = set_instance.to_dict()
            set_data['collection_count'] = collection_count if collection_count else 0
            set_data['collection_percentage'] = (set_data['collection_count'] / set_instance.card_count) * 100 if set_instance.card_count else 0
            set_data['total_value'] = round(total_value, 2) if total_value else 0.0
            sets_list.append(set_data)

        # Build response
        response = {
            'sets': sets_list,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any Decimal objects to float
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 300, serialized_data)  # Cache for 5 minutes

        logger.info(f"Returning response with {len(sets_list)} sets")
        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred in get_collection_sets: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": "An internal server error occurred. Please try again later."}), 500

@card_routes.route('/collection/<string:card_id>', methods=['POST', 'PUT'])
def update_collection(card_id):
    data = request.json
    quantity_regular = data.get('quantity_regular', 0)
    quantity_foil = data.get('quantity_foil', 0)

    card = Card.query.get(card_id)
    if not card:
        return jsonify({"error": "Card not found."}), 404

    old_set_code = card.set_code
    card.quantity_collection_regular = quantity_regular
    card.quantity_collection_foil = quantity_foil

    db.session.commit()

    # Invalidate specific caches
    current_app.redis_client.delete(f"collection:*:set_code:{old_set_code}")
    current_app.redis_client.delete(f"collection_sets:*:set_code:{old_set_code}")
    current_app.redis_client.delete("collection_stats")

    card_data = card.to_dict()
    card_data.update({
        'quantity_regular': card.quantity_collection_regular,
        'quantity_foil': card.quantity_collection_foil
    })

    return current_app.response_class(
        response=orjson.dumps(card_data).decode(),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/collection/stats', methods=['GET'])
def get_collection_stats():
    cache_key = "collection_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
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

        serialized_data = orjson.dumps(result).decode()
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
    rarities = request.args.getlist('rarities') + request.args.getlist('rarities[]')
    colors = request.args.getlist('colors') + request.args.getlist('colors[]')
    types = request.args.getlist('types') + request.args.getlist('types[]')
    keyword = request.args.get('keyword', '', type=str)

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
                Card.quantity_collection_foil,
                Card.type_line,
                Card.colors,
                Card.keywords
            )
        ).filter(Card.set_code == set_code)

        # Apply filters
        if name:
            query = query.filter(Card.name.ilike(f'%{name}%'))
        if rarities:
            query = query.filter(Card.rarity.in_(rarities))
        if colors:
            VALID_COLORS = {'W', 'U', 'B', 'R', 'G', 'C'}
            invalid_colors = set(colors) - VALID_COLORS
            if invalid_colors:
                return jsonify({"error": f"Invalid colors: {', '.join(invalid_colors)}"}), 400

            # Handle "C" for colorless cards
            if 'C' in colors:
                colors.remove('C')
                # Filter for colorless cards where the 'colors' array is empty
                colorless_filter = func.jsonb_array_length(Card.colors) == 0
            else:
                colorless_filter = None

            # Build the colors filter for colored cards
            if colors:
                colors_filter = Card.colors.overlap(colors)
                if colorless_filter is not None:
                    final_colors_filter = or_(colors_filter, colorless_filter)
                else:
                    final_colors_filter = colors_filter
            else:
                # Only colorless cards are selected
                final_colors_filter = colorless_filter

            # Apply the final colors filter
            if final_colors_filter is not None:
                query = query.filter(final_colors_filter)
        if types:
            type_filters = [Card.type_line.ilike(f'%{type_}%') for type_ in types]
            query = query.filter(or_(*type_filters))
        if keyword:
            query = query.filter(Card.keywords.contains([keyword]))

        # Sort by collector number as integer
        query = query.order_by(func.cast(func.regexp_replace(Card.collector_number, '[^0-9]', '', 'g'), db.Integer))

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
                'quantity_foil': card.quantity_collection_foil,
                'type_line': card.type_line,
                'colors': card.colors,
                'keywords': card.keywords
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
        logger.info(f"import_collection_csv: Successfully parsed CSV file: {file.filename}")
    except Exception as e:
        logger.error(f"import_collection_csv: Failed to parse CSV: {str(e)}")
        return jsonify({"error": f"Failed to parse CSV: {str(e)}"}), 400

    required_columns = {
        'Name', 'Edition', 'Edition code', "Collector's number",
        'Price', 'Foil', 'Currency', 'Scryfall ID', 'Quantity'
    }
    if not required_columns.issubset(set(df.columns)):
        missing = required_columns - set(df.columns)
        logger.error(f"import_collection_csv: CSV is missing columns: {', '.join(missing)}")
        return jsonify({"error": f"CSV is missing columns: {', '.join(missing)}"}), 400

    df['Foil'] = df['Foil'].fillna(False).replace('', False)
    logger.debug("import_collection_csv: Preprocessed 'Foil' column in CSV")

    try:
        updates = process_collection_csv(df)
        db.session.bulk_update_mappings(Card, updates)
        db.session.commit()
        logger.info(f"import_collection_csv: Successfully imported CSV with {len(updates)} updates")

        # Invalidate related caches
        current_app.redis_client.delete("collection:*")
        current_app.redis_client.delete("collection_sets:*")
        current_app.redis_client.delete("collection_stats")
        logger.debug("import_collection_csv: Invalidated related caches")

        return jsonify({"message": "CSV imported successfully", "updates": len(updates)}), 200

    except ValueError as e:
        logger.error(f"import_collection_csv: Error processing CSV: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"import_collection_csv: Database error during CSV import: {str(e)}")
        return jsonify({"error": "A database error occurred. Please try again later."}), 500

def process_collection_csv(df):
    updates = []
    for index, row in df.iterrows():
        scryfall_id = row['Scryfall ID']
        card_name = row['Name']
        try:
            quantity = int(row['Quantity'])
            if quantity < 1:
                raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")
        except ValueError:
            raise ValueError(f"Invalid quantity for card '{card_name}' at row {index + 2}.")

        foil = row['Foil']
        if not isinstance(foil, bool):
            raise ValueError(f"Foil value must be boolean for card '{card_name}' at row {index + 2}.")

        updates.append({
            'id': scryfall_id,
            'quantity_collection_foil': db.func.coalesce(Card.quantity_collection_foil, 0) + (quantity if foil else 0),
            'quantity_collection_regular': db.func.coalesce(Card.quantity_collection_regular, 0) + (quantity if not foil else 0)
        })

    return updates

# Kiosk Routes

@card_routes.route('/kiosk', methods=['GET'])
def get_kiosk():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    cache_key = f"kiosk:page:{page}:per_page:{per_page}"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
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

    serialized_data = orjson.dumps(result).decode()
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
            response=cached_data.decode(),
            status=200,
            mimetype='application/json'
        )

    try:
        kiosk_sets = db.session.query(Set).\
            join(Card, Card.set_code == Set.code).\
            filter((Card.quantity_kiosk_regular > 0) | (Card.quantity_kiosk_foil > 0)).\
            distinct()

        if sort_by == 'released_at':
            if sort_order == 'desc':
                kiosk_sets = kiosk_sets.order_by(Set.released_at.desc())
            else:
                kiosk_sets = kiosk_sets.order_by(Set.released_at)
        else:
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

            kiosk_percentage = (kiosk_count / set_obj.card_count) * 100 if set_obj.card_count > 0 else 0

            # Calculate total_value for the set
            total_value_query = db.session.query(
                func.sum(
                    (func.cast((Card.prices['usd'].astext).cast(Float), Float) * Card.quantity_kiosk_regular) +
                    (func.cast((Card.prices['usd_foil'].astext).cast(Float), Float) * Card.quantity_kiosk_foil)
                )
            ).filter(Card.set_code == set_obj.code)

            total_value = total_value_query.scalar() or 0.0

            set_dict['kiosk_count'] = kiosk_count
            set_dict['kiosk_percentage'] = kiosk_percentage
            set_dict['total_value'] = round(total_value, 2)

            sets_data.append(set_dict)

        # Convert Decimal objects to float
        sets_data = convert_decimals(sets_data)

        response = {
            'sets': sets_data,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }

        # Convert any remaining Decimal objects in the response
        response = convert_decimals(response)

        serialized_data = orjson.dumps(response).decode()
        current_app.redis_client.setex(cache_key, 600, serialized_data)  # Cache for 10 minutes

        return current_app.response_class(
            response=serialized_data,
            status=200,
            mimetype='application/json'
        )
    except Exception as e:
        error_message = f"An unexpected error occurred: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500

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
            response=cached_data.decode(),
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

    serialized_data = orjson.dumps(result).decode()
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
        response=orjson.dumps(card_data).decode(),
        status=200,
        mimetype='application/json'
    )

@card_routes.route('/kiosk/stats', methods=['GET'])
def get_kiosk_stats():
    cache_key = "kiosk_stats"
    cached_data = current_app.redis_client.get(cache_key)

    if cached_data:
        return current_app.response_class(
            response=cached_data.decode(),
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

        serialized_data = orjson.dumps(result).decode()
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
@card_routes.route('/cache_stats', methods=['GET'])
def get_cache_stats():
    total_calls = int(current_app.redis_client.get('cache_total_calls') or 0)
    hits = int(current_app.redis_client.get('cache_hits') or 0)
    misses = int(current_app.redis_client.get('cache_misses') or 0)

    hit_rate = (hits / total_calls * 100) if total_calls > 0 else 0

    response_times = current_app.redis_client.lrange('cache_response_times', 0, -1)
    avg_response_time = sum(float(t) for t in response_times) / len(response_times) if response_times else 0

    return jsonify({
        'total_calls': total_calls,
        'hits': hits,
        'misses': misses,
        'hit_rate': f"{hit_rate:.2f}%",
        'avg_response_time': f"{avg_response_time:.4f} seconds"
    })

@card_routes.route('/collection/sets/<string:set_code>', methods=['GET'])
def get_collection_set(set_code):
    try:
        # Fetch the set instance
        set_instance = Set.query.filter_by(code=set_code).first()
        if not set_instance:
            return jsonify({"error": "Set not found."}), 404

        # Serialize set data
        set_data = set_instance.to_dict()

        # Include additional data such as collection counts
        set_data['collection_count'] = set_instance.collection_count.collection_count if set_instance.collection_count else 0
        set_data['collection_percentage'] = (set_data['collection_count'] / set_instance.card_count) * 100 if set_instance.card_count else 0

        # Fetch cards for this set
        cards = Card.query.filter_by(set_code=set_code).all()
        set_data['cards'] = [card.to_dict() for card in cards]

        return jsonify({
            "set": set_data,
            "cards": set_data['cards']
        }), 200
    except Exception as e:
        error_message = f"An error occurred while fetching the set: {str(e)}"
        logger.exception(error_message)
        return jsonify({"error": error_message}), 500
