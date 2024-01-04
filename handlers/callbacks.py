import re

from aiogram import types
from dispatcher import dp

from actions.start import Start
from actions.auth import LogOut
from actions.client import Accounts

from handlers.ratelimit import rate_limit


@dp.callback_query_handler(lambda c: c.data == "new_token", chat_type=types.ChatType.PRIVATE)
@rate_limit(4, "new_token_button")
async def new_token_button(callback_query: types.CallbackQuery):
    return await Start(callback_query.message).process()


@dp.callback_query_handler(lambda c: c.data == "logout_session", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "logout_button")
async def logout_button(callback_query: types.CallbackQuery):
    return await LogOut(callback_query.message).process()


@dp.callback_query_handler(lambda c: c.data == "accounts_button", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "accounts_button")
async def accounts_button(callback_query: types.CallbackQuery):
    return await Accounts(callback_query.message).process()


@dp.callback_query_handler(
    lambda c: re.match(r"get_account_info_(.*?)_([A-Z]*$)", c.data),
    chat_type=types.ChatType.PRIVATE
)
@rate_limit(1, "select_account_button")
async def select_account_button(callback_query: types.CallbackQuery):
    return await Accounts(callback_query).process()
