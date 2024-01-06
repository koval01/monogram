import re

from aiogram import types
from dispatcher import dp

from actions.start import Start
from actions.auth import LogOut
from actions.client import Accounts

from handlers.ratelimit import rate_limit


@dp.callback_query_handler(
    lambda c: c.data == "new_token",
    chat_type=types.ChatType.PRIVATE
)
@rate_limit(4, "new_token_button")
async def new_token_button(callback_query: types.CallbackQuery) -> types.Message:
    """
    Handle the callback query for the "new_token" button in private chats.

    Args:
        callback_query (types.CallbackQuery): The incoming callback query.

    Returns:
        types.Message: The result of processing the "new_token" button.
    """

    return await Start(callback_query.message).process()


@dp.callback_query_handler(
    lambda c: c.data == "logout_session",
    chat_type=types.ChatType.PRIVATE
)
@rate_limit(1, "logout_button")
async def logout_button(callback_query: types.CallbackQuery) -> types.Message:
    """
    Handle the callback query for the "logout_session" button in private chats.

    Args:
        callback_query (types.CallbackQuery): The incoming callback query.

    Returns:
        types.Message: The result of processing the "logout_session" button.
    """

    return await LogOut(callback_query.message).process()


@dp.callback_query_handler(
    lambda c: c.data == "accounts_button",
    chat_type=types.ChatType.PRIVATE
)
@rate_limit(1, "accounts_button")
async def accounts_button(callback_query: types.CallbackQuery) -> types.Message:
    """
    Handle the callback query for the "accounts_button" button in private chats.

    Args:
        callback_query (types.CallbackQuery): The incoming callback query.

    Returns:
        types.Message: The result of processing the "accounts_button" button.
    """

    return await Accounts(callback_query.message).process()


@dp.callback_query_handler(
    lambda c: re.match(r"get_account_info_(.*?)_([A-Z]*$)", c.data),
    chat_type=types.ChatType.PRIVATE
)
@rate_limit(1, "select_account_button")
async def select_account_button(callback_query: types.CallbackQuery) -> types.Message:
    """
    Handle the callback query for selecting an account in private chats.

    Args:
        callback_query (types.CallbackQuery): The incoming callback query.

    Returns:
        types.Message: The result of processing the account selection.
    """
    
    return await Accounts(callback_query).process()
