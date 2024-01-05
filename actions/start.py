from aiogram import types
from aiogram.types import ChatActions

from actions.auth import RollIn

from dispatcher import bot

from misc.lang import Lang

from decorators import async_timer


class Start:

    def __init__(self, message: types.Message) -> None:
        self.message = message

    @async_timer
    async def check_language(self) -> None:
        if not Lang.lang_check(self.message):
            await self.message.answer(await Lang.get("default_language", self.message))

    @async_timer
    async def process(self) -> types.Message:
        await self.check_language()
        await bot.send_chat_action(self.message.chat.id, ChatActions.TYPING)
            
        return await RollIn(self.message).process()
