from aiogram import types
from dispatcher import dp

from actions.start import Start
from actions.auth import LogOut
from actions.basic import CheckProto, Sys
from actions.client import Accounts

from misc.lang import Lang

from handlers.ratelimit import rate_limit


@dp.message_handler(commands="start", chat_type=types.ChatType.PRIVATE)
@rate_limit(4, "start")
async def cmd_start(message: types.Message) -> types.Message:
    """
    Handle the /start command in private chats.

    This command is used to request authorization, check authorization, or restart the bot

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /start command.
    """

    return await Start(message).process()


@dp.message_handler(commands="logout", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "logout")
async def cmd_logout(message: types.Message) -> types.Message:
    """
    Handle the /logout command in private chats.

    This command is used to end a user's session.
    The bot forgets the authorization token and no longer uses it

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /logout command.
    """

    return await LogOut(message).process()


@dp.message_handler(commands="accounts", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "accounts")
async def cmd_accounts(message: types.Message) -> types.Message:
    """
    Handle the /accounts command in private chats.

    This command calls up a list of user accounts, both cards and, for example, accounts of an Entrepreneur

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /accounts command.
    """

    return await Accounts(message).process()


@dp.message_handler(is_owner=True, commands="check-proto")
async def cmd_check_proto(message: types.Message) -> types.Message:
    """
    Handle the /check-proto command for the owner.

    This command calls up information about the server through which communication with monobank is carried out

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /check-proto command.
    """

    return await CheckProto(message).process()


@dp.message_handler(is_owner=True, commands="sys")
async def cmd_sys(message: types.Message) -> types.Message:
    """
    Handle the /sys command for the owner.

    This command displays information about the bot's environment and package versions

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /sys command.
    """

    return await Sys(message).process()


@dp.message_handler(is_owner=True, commands="ping")
async def cmd_ping_bot(message: types.Message) -> types.Message:
    """
    Handle the /ping command for the owner.

    This command simply returns a plain text message.
    This is the basic method of checking the functionality of the bot

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the /ping command.
    """

    return await message.reply("👊 Up & Running!")


@dp.message_handler(content_types=types.ContentType.ANY)
@rate_limit(1, 'any_data')
async def any_data(message: types.Message) -> types.Message:
    """
    Handle any data received that doesn't match specific command or content types.

    Args:
        message (types.Message): The incoming Telegram message.

    Returns:
        types.Message: The result of processing the any data received.
    """

    return await message.reply(await Lang.get("unknown_request", message))
