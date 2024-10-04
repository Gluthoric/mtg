from typing import Any, Dict, List, Union
from functools import wraps
from flask import current_app, request, jsonify, Response
from decimal import Decimal
import orjson
import logging
from time import time

logger = logging.getLogger(__name__)

def safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def convert_decimals(obj: Any) -> Union[float, Dict, List, Any]:
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

def cache_response(timeout: int = 300):
    """
    Cache the response of a route for a given timeout period.

    Args:
        timeout (int): The timeout in seconds for the cache. Defaults to 300 seconds.

    Returns:
        A decorator that caches the response.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            sorted_args = orjson.dumps(sorted(request.args.items()))
            cache_key = f"{func.__name__}:{request.full_path}:{sorted_args}"
            redis_client = current_app.redis_client

            # Attempt to retrieve cached data
            cached_data = redis_client.get(cache_key)
            if cached_data:
                logger.info(f"Cache hit for key: {cache_key}")
                return current_app.response_class(
                    response=cached_data,
                    status=200,
                    mimetype='application/json'
                )

            # Cache miss, proceed with executing the function
            logger.info(f"Cache miss for key: {cache_key}")
            start_time = time()
            try:
                # Execute the original view function
                response = func(*args, **kwargs)
                end_time = time()

                # Determine if response is tuple (data, status_code)
                if isinstance(response, tuple):
                    data, status_code = response
                else:
                    data = response
                    status_code = 200  # Default to 200 if not specified

                # Only cache successful responses
                if 200 <= status_code < 300:
                    data_serialized = orjson.dumps(data).decode('utf-8')
                    redis_client.setex(cache_key, timeout, data_serialized)
                    logger.info(f"Cached response for key: {cache_key} with timeout: {timeout}")

                # Return the response as a Flask Response object
                return jsonify(data), status_code
            except Exception as e:
                logger.exception(f"Error in {func.__name__}: {str(e)}")
                raise
            finally:
                # Log the response time
                logger.info(f"Response time for {func.__name__}: {end_time - start_time:.4f} seconds")
        return wrapper
    return decorator


def serialize_cards(cards: List[Any], quantity_type: str = 'collection') -> List[Dict]:
    return [card.to_dict(quantity_type=quantity_type) for card in cards]
