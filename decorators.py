import asyncio

import logging as log

from time import time


def async_timer(func):
    """
    Async decorator for order execute time function
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
        return result

    return helper
