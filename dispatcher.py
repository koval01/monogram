import logging
import sentry_sdk

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from filters import IsOwnerFilter
from middleware import ThrottlingMiddleware, AnalyticsMiddleware

import config

# Configure logging
logging.basicConfig(level=logging.INFO)

# error tracker
# if SENTRY_DSN is not specified, this module will be skipped
sentry_sdk.init(
    dsn=config.SENTRY_DSN,
    traces_sample_rate=1.0
)

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
dp.middleware.setup(AnalyticsMiddleware())
