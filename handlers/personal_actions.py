from aiogram import types
from dispatcher import dp

from actions.start import Start
from actions.auth import LogOut
from actions.basic import CheckProto

from handlers.ratelimit import rate_limit


@dp.message_handler(commands="start")
@rate_limit(3, "start")
async def cmd_start(message: types.Message) -> types.Message:
    return await Start(message).process()


@dp.message_handler(commands="logout")
@rate_limit(2, "logout")
async def cmd_logout(message: types.Message) -> types.Message:
    return await LogOut(message).process()


@dp.message_handler(is_owner=True, commands="check-proto")
async def cmd_check_proto(message: types.Message) -> types.Message:
    return await CheckProto(message).process()


@dp.message_handler(is_owner=True, commands="ping")
async def cmd_ping_bot(message: types.Message) -> types.Message:
    return await message.reply("👊 Up & Running!")
