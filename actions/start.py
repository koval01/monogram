from aiogram import types
from aiogram.types import ChatActions

from actions.auth import RollIn

from dispatcher import bot

from misc.lang import Lang

from decorators import async_timer


class Start:

    def __init__(self, message: types.Message) -> None:
        """
        Initializes a Start instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the /start command.
        """

        self.message = message

    @async_timer
    async def check_language(self) -> None:
        """
        Checks and sets the language for the user if not already set to the default language.
        """

        if not Lang.lang_check(self.message):
            await self.message.answer(await Lang.get("default_language", self.message))

    async def process(self) -> types.Message:
        """
        Initiates the processing of the /start command, including language checking and user authentication.

        Returns:
            types.Message: The result of processing the /start command.
        """
        
        await self.check_language()
        await bot.send_chat_action(self.message.chat.id, ChatActions.TYPING)
            
        return await RollIn(self.message).process()
