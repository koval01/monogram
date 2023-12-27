from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from misc.mono import Mono
from misc.models.client_info import Model as ClientModel, Account

from misc.redis_storage import RedisStorage

from misc.lang import Lang


class Accounts:

    def __init__(self, message: types.Message) -> None:
        self.message = message
        
    @property
    async def client(self) -> ClientModel:
        return await Mono.client_info(self.message, await self.token)
    
    @property
    async def token(self) -> str | None:
        return await RedisStorage().get(f"mono_auth_{self.message.chat.id}")
    
    def keyboard_create(self, accounts: list[Account]) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        for account in accounts:
            keyboard.add(
                InlineKeyboardButton(
                    text=Lang.get("card", self.message) % (account.type.title(), account.currencyCode),
                    callback_data=f"get_account_info_{account.type}_{account.currencyCode}"
                )
            )

        return keyboard

    async def get_list(self) -> list[Account]:
        client = await self.client
        return client.accounts

    async def process(self) -> types.Message:
        accounts = await self.get_list()
        return await self.message.reply(
            repr(accounts), reply_markup=self.keyboard_create(accounts)
        )
