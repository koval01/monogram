import asyncio

import logging as log

from time import time


def async_timer(func):
    """
    Async decorator for measuring the execution time of a function.

    Args:
        func (callable): The function to be decorated.

    Returns:
        callable: The decorated function.

    Usage:
    @async_timer
    async def example_function():
        # Your asynchronous function code here

    The decorator logs the execution time of the decorated function
    and issues a warning if the execution time exceeds 500 milliseconds.

    """

    f_name = f"{func.__module__}.{func.__name__}"

    async def process(_, *args, **params):
        if asyncio.iscoroutinefunction(func):
            log.debug(f"AsyncTimer_ {f_name} coroutine function, all ok")
            return await func(*args, **params)
        
        log.error(f"{f_name} not coroutine!")
        return func(*args, **params)

    async def helper(*args, **params):
        start = time()
        result = await process(func, *args, **params)

        f_time = int(round(time() - start, 3) * 1000)
        log.debug(f"Function {f_name} took {f_time} ms")

        if f_time > 500:
            log.warning(f"Function {f_name} was executed inefficiently. Execution time {f_time} ms")

        return result

    return helper
