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
    return await Start(message).process()


@dp.message_handler(commands="logout", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "logout")
async def cmd_logout(message: types.Message) -> types.Message:
    return await LogOut(message).process()


@dp.message_handler(commands="accounts", chat_type=types.ChatType.PRIVATE)
@rate_limit(1, "accounts")
async def cmd_accounts(message: types.Message) -> types.Message:
    return await Accounts(message).process()


@dp.message_handler(is_owner=True, commands="check-proto")
async def cmd_check_proto(message: types.Message) -> types.Message:
    return await CheckProto(message).process()


@dp.message_handler(is_owner=True, commands="sys")
async def cmd_sys(message: types.Message) -> types.Message:
    return await Sys(message).process()


@dp.message_handler(is_owner=True, commands="ping")
async def cmd_ping_bot(message: types.Message) -> types.Message:
    return await message.reply("👊 Up & Running!")


@dp.message_handler(content_types=types.ContentType.ANY)
@rate_limit(1, 'any_data')
async def any_data(message: types.Message) -> types.Message:
    return await message.reply(await Lang.get("unknown_request", message))
