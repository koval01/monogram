import re
import json

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from misc.mono import Mono

from misc.models.client_info import Model as ClientModel
from misc.models.client_info import Account as AccountModel

from misc.image import ImageProcess
from misc.redis_storage import RedisStorage

from misc.lang import Lang
from misc.other import Other


class Accounts:

    def __init__(self, message: types.Message | types.CallbackQuery) -> None:
        self.message = message
        self.query = None
        
        if type(message) is types.CallbackQuery:
            self.message = message.message
            self.query = message

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
    
    def keyboard_create(self, accounts: list[AccountModel], selected_account: AccountModel) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        check_mark = "☑️"
        
        for account in accounts:
            account_name = account.type.title()
            if account.type == "yellow":
                account_name = Lang.get("yellow", self.message)

            account_name = Lang.get("card", self.message) % (account_name, account.currencyCode)
            if account.type == "fop":
                account_name = "%s %s" % (Lang.get("fop", self.message), account.currencyCode)

            keyboard.add(
                InlineKeyboardButton(
                    text=f"{account_name} {check_mark if account is selected_account else ''}",
                    callback_data=f"get_account_info_{account.type}_{account.currencyCode}"
                )
            )

        return keyboard

    async def get_list(self) -> list[AccountModel]:
        client = await self.client
        return client.accounts

    def _process_query(self, accounts: list[AccountModel]) -> AccountModel | None:
        data = re.search(r"get_account_info_(?P<account_type>.*?)_(?P<currency>[A-Z]*$)", self.query.data).groupdict()
        if not all(k in data.keys() for k in ("account_type", "currency",)):
            return

        if not accounts:
            return

        for account in accounts:
            account: AccountModel
            if account.type == data["account_type"] \
                    and account.currencyCode.upper() == data["currency"].upper():
                return account

    async def process(self) -> types.Message:
        accounts = await self.get_list()

        if self.query:
            selected_account = self._process_query(accounts)
        else:
            selected_account = [a for a in accounts if a.currencyCode == "UAH"][0]

        image = bytes(AccountImage(self.message, selected_account))
        markup = self.keyboard_create(accounts, selected_account)

        if self.query:
            await self.message.delete()

        return await self.message.answer_photo(
            image, reply_markup=markup
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

    def __bytes__(self) -> bytes:
        return self.build_image()
