import base64
import re

from misc.mono import Mono
from misc.lang import Lang
from misc.redis_storage import RedisStorage

from misc.models.roll_in import Model as RollModel
from misc.models.client_info import Model as ClientInfoModel

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from dispatcher import bot


class RollIn:
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
    
    def keyboard_create(self, roll: RollModel) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        keyboard.add(InlineKeyboardButton(
            Lang.get("link_button", self.message), url=roll.url))
        keyboard.add(InlineKeyboardButton(
            Lang.get("check_token_button", self.message), callback_data=f"mono_token_{roll.token}"))
        
        return keyboard

    async def check_auth(self) -> ClientInfoModel | None:
        token = await RedisStorage().get(f"mono_auth_{self.message.chat.id}")

        if not token:
            return

        client = await Mono().client_info(self.message, token)
        return client

    async def process(self) -> types.Message:
        auth_client = await self.check_auth()
        if auth_client:
            return await self.message.reply(Lang.get("welcome_back", self.message) % auth_client.name.split()[-1])

        roll = await Mono().roll_in()

        if not roll:
            return await self.message.reply(Lang.get("roll_error", self.message))

        return await self.message.reply_photo(
            base64.decodebytes(roll.qr), Lang.get("start", self.message),
            reply_markup=self.keyboard_create(roll))


class LogOut:

    def __init__(self, message: types.Message) -> None:
        self.message = message

    async def process(self) -> types.Message:
        storage_flush = await RedisStorage().forget(f"mono_auth_{self.message.chat.id}")

        if not storage_flush:
            return await self.message.reply(Lang.get("unknown_error", self.message))

        return await self.message.reply(Lang.get("logout", self.message))


class CheckToken:

    def __init__(self, callback_query: types.CallbackQuery) -> None:
        self.callback_query = callback_query
        self.token = re.search(r"mono_token_(.*)?", callback_query.data).group(1)
        self.lang = callback_query.message.reply_to_message.from_user.language_code

    async def process(self) -> types.Message | None:
        token = await Mono().check_token(self.token)

        if not token:
            return

        client = await Mono().client_info(self.lang, token)

        message = self.callback_query.message

        if not await RedisStorage().set(f"mono_auth_{message.chat.id}", token):
            return await bot.send_message(
                chat_id=message.chat.id,
                text=Lang.get("update_mono_token_error", message)
            )

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text=Lang.get("mono_token_active", message) % client.name.split()[-1]
        )

        return await bot.answer_callback_query(
            self.callback_query.id,
            text=Lang.get("ok", message)
        )
