from aiogram import types
from dispatcher import dp

from actions.start import Start
from actions.basic import CheckProto


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    return await Start(message).process()


@dp.message_handler(is_owner=True, commands="check-proto")
async def cmd_ping_bot(message: types.Message):
    return await CheckProto(message).process()


@dp.message_handler(is_owner=True, commands="ping")
async def cmd_ping_bot(message: types.Message):
    await message.reply("👊 Up & Running!")
