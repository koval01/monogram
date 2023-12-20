import re

from aiogram import types
from dispatcher import dp

from actions.auth import CheckToken

from handlers.ratelimit import rate_limit


@dp.callback_query_handler(lambda c: re.match(r"mono_token_(.*)?", c.data))
@rate_limit(5, "check_token_button")
async def check_token_button(callback_query: types.CallbackQuery):
    return await CheckToken(callback_query).process()
