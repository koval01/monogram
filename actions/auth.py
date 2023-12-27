import base64
import asyncio

from misc.mono import Mono
from misc.lang import Lang
from misc.redis_storage import RedisStorage

from misc.models.roll_in import Model as RollModel
from misc.models.client_info import Model as ClientInfoModel

from aiogram import types
from aiogram.utils import exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from dispatcher import bot


class RollIn:
    future_list: dict = {}
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
    
    def keyboard_create(self, roll: RollModel) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        keyboard.add(InlineKeyboardButton(
            Lang.get("link_button", self.message), url=roll.url))
        
        return keyboard

    async def check_auth(self) -> ClientInfoModel | None:
        future = RollIn.future_list.get(self.message.chat.id)
        if future:
            future.cancel()

        token = await RedisStorage().get(f"mono_auth_{self.message.chat.id}")

        if not token:
            return

        client = await Mono().client_info(self.message, token)
        return client

    async def process_old(self, new_msg: types.Message) -> None:
        key = f"start_qr_last_{self.message.chat.id}"
        old_msg_id = await RedisStorage().get(key)

        if isinstance(old_msg_id, str):
            try:
                await bot.delete_message(self.message.chat.id, int(old_msg_id))
            except exceptions.MessageToDeleteNotFound:
                pass

        await RedisStorage().set(key, new_msg.message_id)

    @staticmethod
    async def token_check_loop(message: types.Message) -> None:
        for _ in range(15):
            result = await CheckToken(message).process()
            if result:
                return

        button = InlineKeyboardMarkup().add(InlineKeyboardButton(
            Lang.get("try_again", message), callback_data="new_token"))

        await message.reply(Lang.get("token_expired", message), reply_markup=button)
        await message.delete()

    async def process(self) -> types.Message:
        auth_client = await self.check_auth()
        if auth_client:
            return await self.message.reply(
                Lang.get("welcome_back", self.message) % auth_client.name.split()[-1]
            )

        roll = await Mono().roll_in()

        if not roll:
            return await self.message.reply(Lang.get("roll_error", self.message))

        token_set = await RedisStorage().set(f"mono_start_{self.message.chat.id}", roll.token)
        if not token_set:
            return await self.message.reply(Lang.get("update_mono_token_error", self.message))

        msg = await self.message.reply_photo(
            photo=base64.decodebytes(roll.qr),
            caption=Lang.get("start", self.message),
            reply_markup=self.keyboard_create(roll)
        )

        RollIn.future_list[self.message.chat.id] = asyncio.ensure_future(self.token_check_loop(msg))

        await self.process_old(msg)
        return msg


class LogOut:

    def __init__(self, message: types.Message) -> None:
        self.message = message

    async def process(self) -> types.Message:
        storage_flush = await RedisStorage().forget(f"mono_auth_{self.message.chat.id}")

        if not storage_flush:
            return await self.message.reply(Lang.get("unknown_error", self.message))

        return await self.message.reply(Lang.get("logout", self.message))


class CheckToken:

    def __init__(self, message: types.Message) -> None:
        self.message = message
        self.lang = message.from_user.language_code

    async def start_token(self) -> str | None:
        return await RedisStorage().get(f"mono_start_{self.message.chat.id}")

    async def process(self) -> bool:
        start_token = await self.start_token()
        token = await Mono().check_token(start_token)

        if not token:
            return False

        client = await Mono().client_info(self.message, token)

        message = self.message

        if not await RedisStorage().set(f"mono_auth_{message.chat.id}", token):
            await bot.send_message(
                chat_id=message.chat.id,
                text=Lang.get("update_mono_token_error", message)
            )
            return False

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text=Lang.get("mono_token_active", message) % client.name.split()[-1]
        )

        return True
