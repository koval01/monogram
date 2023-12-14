import re

from aiogram import types
from dispatcher import dp

from actions.auth import CheckToken


@dp.callback_query_handler(lambda c: re.match(r"mono_token_(.*)?", c.data))
async def check_token_button(callback_query: types.CallbackQuery):
    return await CheckToken(callback_query).process()
