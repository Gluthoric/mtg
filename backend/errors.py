from flask import jsonify

def handle_error(status_code, message):
    """Create a JSON response for errors."""
    response = jsonify({'error': message})
    response.status_code = status_code
    return response
