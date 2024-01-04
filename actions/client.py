import re
import json

from time import time

from textwrap import wrap

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from PIL import Image

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
    
    async def keyboard_create(
            self, accounts: list[AccountModel], selected_account: AccountModel
    ) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        check_mark = "☑️"
        
        accounts = sorted(accounts, key=lambda k: (k.type, k.currencyCode))
        for account in accounts:
            account_name = account.type.title()
            if account.type == "yellow":
                account_name = await Lang.get("yellow", self.message)

            account_name = await Lang.get("card", self.message) % (account_name, account.currencyCode)
            if account.type == "fop":
                account_name = "%s %s" % (await Lang.get("fop", self.message), account.currencyCode)

            keyboard.add(
                InlineKeyboardButton(
                    text=f"{account_name} {check_mark if account is selected_account else ''}",
                    callback_data=f"get_account_info_{account.type}_{account.currencyCode}"
                )
            )

        return keyboard

    async def get_list(self) -> (list[AccountModel], AccountModel):
        client = await self.client
        return client.accounts, client

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

    async def storage(self, account: AccountModel, message: types.Message = None) -> str | None:
        key = f"acc_{account.type}_{account.currencyCode}_{self.message.chat.id}"
        balance = int(account.balance*100)

        id_buff = await RedisStorage().get(key)

        if id_buff:
            kv = json.loads(id_buff)
            if balance == kv["balance"]:
                return kv["file_id"]

        if not message:
            return

        photo_list = message.photo
        if not photo_list:
            return

        photo_list = sorted(photo_list, key=lambda k: -k.file_size)
        id_buff_var = {
            "file_id": photo_list[0].file_id,
            "balance": balance,
            "timestamp": int(time())
        }
        await RedisStorage().set(key, json.dumps(id_buff_var), ex=1800)

        return None

    async def process(self) -> types.Message:
        accounts, client = await self.get_list()

        if self.query:
            selected_account = self._process_query(accounts)
        else:
            selected_account = [a for a in accounts if a.currencyCode == "UAH"][0]

        image = await AccountImage(self.message, selected_account, client.name).result()
        markup = await self.keyboard_create(accounts, selected_account)

        file_id = await self.storage(selected_account)
        if file_id:
            image = file_id

        if self.query:
            await self.message.delete()

        answ_photo = await self.message.answer_photo(
            image, reply_markup=markup
        )

        await self.storage(selected_account, answ_photo)
        return answ_photo


class AccountImage:

    def __init__(self, message: types.Message, account: AccountModel, client_name: str) -> None:
        self.message = message
        self.account = account
        self.client_name = client_name

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

    @property
    def card(self) -> Image:
        card = ImageProcess(f"{self.account.type}-card.png")

        card.add_text(  # card holder
            text=self.client_name,
            pos=(42, 298),
            color={
                "black": (255, 255, 255),
                "white": (0, 0, 0),
                "yellow": (0, 0, 0)
            }[self.account.type],
            font=self.fonts["medium"],
            size=26, align="left"
        ) if self.account.type in ["black", "white", "platinum", "iron", "yellow"] else None

        card.add_text(  # currency
            text=self.account.currencyCode,
            pos=(482, 40),
            color=(115, 115, 115),
            font=self.fonts["regular"],
            size=24, align="left"
        ) if self.account.type == "black" else None

        # build and paste card system logo on client card
        card_number = int(self.account.maskedPan[0].replace("*", "0"))
        card_system_name = Other.identify_credit_card(card_number)

        card_system = ImageProcess("%s-logo%s.png" % (
            card_system_name.lower(),
            "-%s" %
            ("white" if self.account.type in ("black", "platinum", "iron", "rebuilding", "atb",)
             else "black") if card_system_name == "VISA" else ""
        ))

        card_sys = card_system.image
        card.image.paste(card_sys, (440, 270), card_sys)

        card.perspective(-.3)
        card.image = card.image.rotate(10, resample=Image.BICUBIC, expand=True)

        return card

    @property
    def background(self) -> str:
        if self.account.type in ("black", "platinum", "iron", "fop",):
            return "%s_background.png" % self.account.currencyCode

        return f"{self.account.type}_card_background.png"

    async def build_image(self) -> bytes:
        background = ImageProcess(self.background)
        background.add_text(  # total balance
            text=self.int_display(self.account.balance, self.account.currencyCode),
            pos=(0, 45),
            color=(255, 255, 255),
            font=self.fonts["bold"],
            size=120, align="center"
        )

        # pan
        if self.account.maskedPan:
            masked_pan = " ".join(wrap(self.account.maskedPan[0], 4))
            _ = masked_pan

        if self.account.creditLimit:
            vl = 420
            vl_i = 695
            f_size = 23
            font = "regular"
            color_tone = 222

            ow_h = 190
            cd_h = 225

            # own funds
            background.add_text(
                text=await Lang.get("own_funds", self.message),
                pos=(vl, ow_h),
                color=(color_tone,)*3,
                font=self.fonts[font],
                size=f_size, align="left"
            )
            background.add_text(
                text=self.int_display((self.account.balance - self.account.creditLimit), self.account.currencyCode),
                pos=(vl_i, ow_h),
                color=(color_tone,)*3,
                font=self.fonts[font],
                size=f_size, align="right"
            )

            # credit limit
            background.add_text(
                text=await Lang.get("credit_limit", self.message),
                pos=(vl, cd_h),
                color=(color_tone,)*3,
                font=self.fonts[font],
                size=f_size, align="left"
            )
            background.add_text(
                text=self.int_display(self.account.creditLimit, self.account.currencyCode),
                pos=(vl_i, cd_h),
                color=(color_tone,)*3,
                font=self.fonts[font],
                size=f_size, align="right"
            )

        # paste client card
        card = self.card.image
        background.image.paste(card, (300, 240), card)

        # decoration
        cat = ImageProcess("sitting_cat.png").image
        background.image.paste(cat, (950, 420), cat)

        return bytes(background)

    async def result(self) -> bytes:
        return await self.build_image()
