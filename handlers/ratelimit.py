def rate_limit(limit: int, key=None):
    """
    Decorator for configuring rate limit and key in different functions.

    This decorator allows configuring rate limits for different functions. The 'limit' parameter specifies the maximum
    number of times the decorated function can be called within a given time period. The 'key' parameter, if provided,
    sets a specific key for rate limiting purposes.

    Args:
        limit (int): The maximum number of allowed calls within the specified time period.
        key (Optional[Any]): An optional key to associate with the rate limit. Defaults to None.

    Returns:
        Callable: The decorated function with rate limit and key configuration.

    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator
