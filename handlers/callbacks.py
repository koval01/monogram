import re

from aiogram import types
from dispatcher import dp

from actions.start import Start

from handlers.ratelimit import rate_limit


@dp.callback_query_handler(lambda c: c.data == "new_token")
@rate_limit(3, "new_token_button")
async def new_token_button(callback_query: types.CallbackQuery):
    return await Start(callback_query.message).process()
