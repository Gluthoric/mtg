# utils.py
"""
This module contains utility functions used throughout the application.
It provides helpers for type conversion, caching, and serialization.
"""

from typing import Any, Dict, List, Union
from functools import wraps
from flask import current_app, request
from decimal import Decimal
import orjson
import logging
from time import time

logger = logging.getLogger(__name__)

def safe_float(value: Any) -> float:
    """
    Convert value to float safely.
    
    Args:
        value (Any): The value to convert.
    
    Returns:
        float: The converted float value, or 0.0 if conversion fails.
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def convert_decimals(obj: Any) -> Union[float, Dict, List, Any]:
    """
    Recursively convert Decimal objects to float in a data structure.
    
    Args:
        obj (Any): The object to convert.
    
    Returns:
        Union[float, Dict, List, Any]: The converted object.
    """
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def cache_response(timeout: int = 300):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{request.full_path}:{orjson.dumps(request.args)}"
            redis_client = current_app.redis_client

            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return current_app.response_class(
                    response=cached_data,
                    status=200,
                    mimetype='application/json'
                )

            logger.info(f"Cache miss for key: {cache_key}")
            start_time = time()
            try:
                response = func(*args, **kwargs)
                end_time = time()
                
                if isinstance(response, tuple):
                    data, status_code = response
                else:
                    data, status_code = response.get_json(), response.status_code

                if 200 <= status_code < 300:
                    # Convert data to string if it's not already
                    if not isinstance(data, (str, bytes)):
                        data = orjson.dumps(data).decode('utf-8')
                    redis_client.setex(cache_key, timeout, data)
                    logger.info(f"Cached response for key: {cache_key} with timeout: {timeout}")
                
                # Log response time
                logger.info(f"Response time for {func.__name__}: {end_time - start_time:.4f} seconds")
                
                return response
            except Exception as e:
                logger.exception(f"Error in {func.__name__}: {str(e)}")
                raise
        return wrapper
    return decorator

def serialize_cards(cards: List[Any], quantity_type: str = 'collection') -> List[Dict]:
    """
    Serialize a list of card objects.
    
    Args:
        cards (List[Any]): The list of card objects to serialize.
        quantity_type (str): The type of quantity to use. Defaults to 'collection'.
    
    Returns:
        List[Dict]: The serialized list of cards.
    """
    return [card.to_dict(quantity_type=quantity_type) for card in cards]
