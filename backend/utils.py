# utils.py
"""
This module contains utility functions used throughout the application.
It provides helpers for type conversion, caching, and serialization.
"""

import time
from functools import wraps
from flask import current_app, request
from decimal import Decimal
import orjson
import logging

logger = logging.getLogger(__name__)

def safe_float(value):
    """Convert value to float safely."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def convert_decimals(obj):
    """Recursively convert Decimal objects to float in a data structure."""
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def cache_response(timeout=300):
    """Decorator to cache the response of a route."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{request.full_path}"
            redis_client = current_app.redis_client

            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for key: {cache_key}")
                return current_app.response_class(
                    response=cached_data,
                    status=200,
                    mimetype='application/json'
                )

            response = func(*args, **kwargs)
            redis_client.setex(cache_key, timeout, response.get_data())
            return response
        return wrapper
    return decorator

def serialize_cards(cards, quantity_type='collection'):
    """Serialize a list of card objects."""
    return [card.to_dict(quantity_type=quantity_type) for card in cards]