import asyncio

from misc.mono import Mono
from misc.lang import Lang
from misc.redis_storage import RedisStorage

from misc.models.roll_in import Model as RollModel
from misc.models.client_info import Model as ClientInfoModel

from misc.image import ImageProcess

from aiogram import types, exceptions
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from dispatcher import bot

from decorators import async_timer


class QRImage:

    def __init__(self, roll: RollModel, background: str = "monocat_auth.png") -> None:
        self.roll = roll
        self.image_back = ImageProcess(background)
        self.image_qr = ImageProcess(roll.qr)

    def _link_preview(self) -> None:
        url = self.roll.url.split("//")[1]
        self.image_back.add_text(
            text=url,
            pos=(0, 600),
            color=(0, 0, 0),
            font="Montserrat-Regular.ttf",
            size=12,
            align="center"
        )

    @property
    def get(self) -> bytes:
        self.image_back.image.paste(
            self.image_qr.image,
            (185, 380)
        )
        self._link_preview()
        return bytes(self.image_back)


class RollIn:
    future_list: dict = {}
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
    
    async def keyboard_create(self, roll: RollModel) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        keyboard.add(InlineKeyboardButton(
            await Lang.get("link_button", self.message), url=roll.url))
        
        return keyboard

    @async_timer
    async def check_auth(self) -> ClientInfoModel | None:
        future = RollIn.future_list.get(self.message.chat.id)
        if future:
            future.cancel()

        token = await RedisStorage().get(f"mono_auth_{self.message.chat.id}")

        if not token:
            return

        client = await Mono().client_info(self.message, token)
        return client

    @async_timer
    async def process_old_message(self, new_msg: types.Message) -> None:
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
            await Lang.get("try_again", message), callback_data="new_token"))

        await message.answer(await Lang.get("token_expired", message), reply_markup=button)

        try:
            await message.delete()
        except exceptions.MessageToDeleteNotFound:
            pass

    @staticmethod
    async def session_buttons(message: types.Message) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(await Lang.get("accounts_button", message), callback_data="accounts_button"))
        keyboard.add(InlineKeyboardButton(await Lang.get("logout_button", message), callback_data="logout_session"))

        return keyboard

    @async_timer
    async def process(self) -> types.Message:
        auth_client = await self.check_auth()
        if auth_client:
            return await self.message.reply(
                text=await Lang.get("welcome_back", self.message) % auth_client.name.split()[-1],
                reply_markup=await self.session_buttons(self.message)
            )

        roll = await Mono().roll_in()

        if not roll:
            return await self.message.reply(await Lang.get("roll_error", self.message))

        token_set = await RedisStorage().set(f"mono_start_{self.message.chat.id}", roll.token)
        if not token_set:
            return await self.message.reply(await Lang.get("update_mono_token_error", self.message))

        msg = await self.message.reply_photo(
            photo=QRImage(roll).get,
            caption=await Lang.get("start", self.message),
            reply_markup=await self.keyboard_create(roll),
            protect_content=True
        )

        RollIn.future_list[self.message.chat.id] = asyncio.ensure_future(self.token_check_loop(msg))

        await self.process_old_message(msg)
        return msg


class LogOut:

    def __init__(self, message: types.Message) -> None:
        self.message = message

    @async_timer
    async def process(self) -> types.Message:
        storage_flush = await RedisStorage().forget(f"mono_auth_{self.message.chat.id}")

        if not storage_flush:
            return await self.message.reply(await Lang.get("unknown_error", self.message))

        return await self.message.reply(await Lang.get("logout", self.message))


class CheckToken:

    def __init__(self, message: types.Message) -> None:
        self.message = message
        self.lang = message.from_user.language_code

    @async_timer
    async def get_start_token(self) -> str | None:
        return await RedisStorage().get(f"mono_start_{self.message.chat.id}")

    @async_timer
    async def process(self) -> bool:
        start_token = await self.get_start_token()
        token = await Mono().check_token(start_token)

        if not token:
            return False

        client = await Mono().client_info(self.message, token)

        message = self.message

        if not await RedisStorage().set(f"mono_auth_{message.chat.id}", token):
            await bot.send_message(
                chat_id=message.chat.id,
                text=await Lang.get("update_mono_token_error", message)
            )
            return False

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text=await Lang.get("mono_token_active", message) % client.name.split()[-1],
            reply_markup=await RollIn.session_buttons(message)
        )

        return True
