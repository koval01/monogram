import json

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from misc.mono import Mono

from misc.models.client_info import Model as ClientModel, Account
from misc.models.client_info import Account as AccountModel

from misc.image import ImageProcess
from misc.redis_storage import RedisStorage

from misc.lang import Lang
from misc.other import Other


class Accounts:

    def __init__(self, message: types.Message) -> None:
        self.message = message
        
    @property
    async def client(self) -> ClientModel:
        redis_key = f"mono_client_{self.message.chat.id}"
        client = await RedisStorage().get(redis_key)
        if client:
            return ClientModel(**json.loads(client))

        client = await Mono.client_info(self.message, await self.token)
        await RedisStorage().set(redis_key, client.model_dump_json(), ex=60)

        return client
    
    @property
    async def token(self) -> str | None:
        return await RedisStorage().get(f"mono_auth_{self.message.chat.id}")
    
    def keyboard_create(self, accounts: list[Account]) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        for account in accounts:
            account_name = account.type.title()
            if account.type == "yellow":
                account_name = Lang.get("yellow", self.message)

            account_name = Lang.get("card", self.message) % (account_name, account.currencyCode)
            if account.type == "fop":
                account_name = "%s %s" % (Lang.get("fop", self.message), account.currencyCode)

            keyboard.add(
                InlineKeyboardButton(
                    text=account_name,
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


class AccountImage:

    def __init__(self, message: types.Message, account: AccountModel) -> None:
        self.message = message
        self.account = account

        self.background = "background.png"
        self.fonts = {
            "regular": "Montserrat-Regular.ttf",
            "medium": "Montserrat-Medium.ttf",
            "bold": "Montserrat-SemiBold.ttf"
        }
        self.currency_symbols = {
            "UAH": "₴",
            "USD": "$",
            "EUR": "€"
        }

    def int_display(self, value: int | float, currency: str) -> str:
        return "%s %s" % (Other.format_number(value), self.currency_symbols[currency])

    def build_image(self) -> bytes:
        image = ImageProcess(self.background)
        image.add_text(
            text=self.int_display(self.account.balance, self.account.currencyCode),
            pos=(0, 128),
            color=(255, 255, 255),
            font=self.fonts["bold"],
            size=120,
            align="center"
        )
        return bytes(image)

    async def process(self) -> types.Message:
        return await self.message.reply_photo(self.build_image())
