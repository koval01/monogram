import logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from filters import IsOwnerFilter
from middleware import ThrottlingMiddleware
import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# prerequisites
if not config.BOT_TOKEN:
    exit("No token provided")

# init
storage = MemoryStorage()
bot = Bot(token=config.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, storage=storage)

# activate filters
dp.filters_factory.bind(IsOwnerFilter)

# activate middleware
dp.middleware.setup(ThrottlingMiddleware())
