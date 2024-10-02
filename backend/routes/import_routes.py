import pandas as pd
import logging
from flask import Blueprint, jsonify, request, current_app
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from models.card import Card
from database import db

import_routes = Blueprint('import_routes', __name__)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@import_routes.route('/kiosk/import_csv', methods=['POST'])
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


@import_routes.route('/collection/import_csv', methods=['POST'])
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
