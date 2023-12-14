from aiogram import executor, Dispatcher
from dispatcher import dp

from misc.lang import Lang
from misc.redis_storage import RedisStorage

import handlers


async def startup(_: Dispatcher) -> None:
    Lang().load()
    RedisStorage().create_cursor()


async def shutdown(_: Dispatcher) -> None:
    await RedisStorage().shutdown()


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=startup, on_shutdown=shutdown)
