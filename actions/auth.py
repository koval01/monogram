import base64
import re

from misc.mono import Mono
from misc.lang import Lang
from misc.redis_storage import RedisStorage

from misc.models.roll_in import Model as RollModel

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from dispatcher import bot

from transliterate import translit


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

    async def process(self) -> types.Message:
        roll = await Mono().roll_in()
        
        if not roll:
            return await self.message.reply(Lang.get("roll_error", self.message))

        return await self.message.reply_photo(
            base64.decodebytes(roll.qr), Lang.get("start", self.message),
            reply_markup=self.keyboard_create(roll))


class CheckToken:

    def __init__(self, callback_query: types.CallbackQuery) -> None:
        self.callback_query = callback_query
        self.token = re.search(r"mono_token_(.*)?", callback_query.data).group(1)
        self.lang = callback_query.message.reply_to_message.from_user.language_code

    def name_translate(self, name: str) -> str:
        if self.lang == "uk":
            return name
        return translit(name, 'uk', reversed=True)

    async def process(self) -> types.Message | None:
        token = await Mono().check_token(self.token)

        if not token:
            return

        client = await Mono().client_info(token)
        client.name = self.name_translate(client.name)

        if not await RedisStorage().set(f"mono_auth_{token}", token):
            return await bot.send_message(
                chat_id=self.callback_query.message.chat.id,
                text=Lang.get("update_mono_token_error", self.callback_query.message)
            )

        await bot.delete_message(
            chat_id=self.callback_query.message.chat.id,
            message_id=self.callback_query.message.message_id
        )

        await bot.send_message(
            chat_id=self.callback_query.message.chat.id,
            text=Lang.get("mono_token_active", self.callback_query.message) % client.name.split()[1]
        )

        return await bot.answer_callback_query(
            self.callback_query.id,
            text=Lang.get("ok", self.callback_query.message)
        )
