from aiogram import executor, Dispatcher
from dispatcher import dp  # Import the Dispatcher instance from the dispatcher module

from misc.lang import Lang  # Import the Lang class for language-related operations
from misc.redis_storage import RedisStorage  # Import the RedisStorage class for handling Redis storage

import handlers  # Import your handlers module with message and callback query handlers

_ = handlers


async def startup(_: Dispatcher) -> None:
    """
    Startup function called on the start of the application.

    Args:
        _: Dispatcher: The Dispatcher instance.

    """
    Lang().load()  # Load language data using the Lang class
    RedisStorage().create_cursor()  # Create a cursor for the Redis storage


async def shutdown(_: Dispatcher) -> None:
    """
    Shutdown function called on the termination of the application.

    Args:
        _: Dispatcher: The Dispatcher instance.

    """
    await RedisStorage().shutdown()  # Shutdown Redis storage


if __name__ == "__main__":
    # Start the polling with the Dispatcher instance, skipping updates, and specifying startup and shutdown functions
    executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
