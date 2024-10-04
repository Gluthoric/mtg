from flask import jsonify
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

from flask import request

def handle_error(status_code: int, message: str, error_type: str) -> Tuple[Dict[str, Any], int]:
    """
    Create a JSON response for errors and log the error.
    
    Args:
        status_code (int): The HTTP status code for the error.
        message (str): The error message.
        error_type (str): The type of error.
    
    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the error response and status code.
    """
    error_details = f"{error_type}: {message}"
    logger.error(f"Error {status_code}: {error_details}")
    logger.error(f"Request: {request.method} {request.url}")
    logger.error(f"Headers: {dict(request.headers)}")
    return {'error': error_details, 'status': status_code}, status_code

class APIError(Exception):
    """Custom exception class for API errors."""
    def __init__(self, message: str, status_code: int, error_type: str = "APIError"):
        self.message = message
        self.status_code = status_code
        self.error_type = error_type
        super().__init__(self.message)

def handle_api_error(error: APIError) -> Tuple[Dict[str, Any], int]:
    """
    Handle APIError exceptions.
    
    Args:
        error (APIError): The APIError instance.
    
    Returns:
        Tuple[Dict[str, Any], int]: A tuple containing the error response and status code.
    """
    return handle_error(error.status_code, error.message, error.error_type)
