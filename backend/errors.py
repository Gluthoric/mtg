from flask import jsonify
import logging

logger = logging.getLogger(__name__)

def handle_error(status_code: int, message: str):
    """Create a JSON response for errors and log the error."""
    logger.error(f"Error {status_code}: {message}")
    response = jsonify({'error': message})
    response.status_code = status_code
    return response
