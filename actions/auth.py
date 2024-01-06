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
        """
        Initializes a QRImage instance.

        Args:
            roll (RollModel): An instance of RollModel representing the QR code and its associated data.
            background (str, optional): File path or name of the background image. Defaults to "monocat_auth.png".
        """

        self.roll = roll
        self.image_back = ImageProcess(background)
        self.image_qr = ImageProcess(roll.qr)

    def _link_preview(self) -> None:
        """
        Adds a link preview text to the background image based on the RollModel URL.
        """

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
        """
        Combines the background image, QR code image, and link preview text to generate a final image.

        Returns:
            bytes: The binary representation of the final image.
        """

        self.image_back.image.paste(
            self.image_qr.image,
            (185, 380)
        )
        self._link_preview()
        return bytes(self.image_back)


class RollIn:
    future_list: dict = {}
    
    def __init__(self, message: types.Message) -> None:
        """
        Initializes a RollIn instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the MonoBank integration process.
        """

        self.message = message
    
    @async_timer
    async def keyboard_create(self, roll: RollModel) -> InlineKeyboardMarkup:
        """
        Creates and returns an inline keyboard for interacting with the MonoBank integration.

        Args:
            roll (RollModel): An instance of RollModel representing MonoBank integration details.

        Returns:
            InlineKeyboardMarkup: The generated inline keyboard.
        """

        keyboard = InlineKeyboardMarkup()
        
        keyboard.add(InlineKeyboardButton(
            await Lang.get("link_button", self.message), url=roll.url))
        
        return keyboard

    @async_timer
    async def check_auth(self) -> ClientInfoModel | None:
        """
        Checks the authentication status and retrieves client information from MonoBank.

        Returns:
            ClientInfoModel | None: The client information if authenticated, otherwise None.
        """

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
        """
        Processes the old message by deleting it if it exists, updating the message ID in Redis storage.

        Args:
            new_msg (types.Message): The new message to be processed.
        """

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
        """
        Performs a looped token check and handles token expiration by sending a prompt to the user.

        Args:
            message (types.Message): The message associated with the MonoBank integration.
        """

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
        """
        Generates an inline keyboard with session-related options.

        Args:
            message (types.Message): The message associated with the MonoBank integration.

        Returns:
            InlineKeyboardMarkup: The generated inline keyboard.
        """

        keyboard = InlineKeyboardMarkup()

        keyboard.add(InlineKeyboardButton(
            await Lang.get("accounts_button", message),
            callback_data="accounts_button")
        )
        keyboard.add(InlineKeyboardButton(
            await Lang.get("logout_button", message),
            callback_data="logout_session")
        )

        return keyboard

    async def process(self) -> types.Message:
        """
        Initiates the MonoBank integration process, handling authentication checks,
        QR code generation, and message replies.

        Returns:
            types.Message: The message representing the result of the integration process.
        """

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
        """
        Initializes a LogOut instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the logout process.
        """

        self.message = message

    async def process(self) -> types.Message:
        """
        Initiates the logout process by clearing the stored authentication token and sending a logout message.

        Returns:
            types.Message: The message representing the result of the logout process.
        """

        await bot.send_chat_action(self.message.chat.id, types.ChatActions.TYPING)

        storage_flush = await RedisStorage().forget(f"mono_auth_{self.message.chat.id}")
        if not storage_flush:
            return await self.message.reply(await Lang.get("unknown_error", self.message))

        return await self.message.reply(await Lang.get("logout", self.message))


class CheckToken:

    def __init__(self, message: types.Message) -> None:
        """
        Initializes a CheckToken instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the token checking process.
        """

        self.message = message
        self.lang = message.from_user.language_code

    @async_timer
    async def get_start_token(self) -> str | None:
        """
        Retrieves the starting token for the MonoBank integration process.

        Returns:
            str | None: The starting token if available, otherwise None.
        """

        return await RedisStorage().get(f"mono_start_{self.message.chat.id}")

    @staticmethod
    @async_timer
    async def _redis_action(message: types.Message, token: str) -> bool:
        """
        Performs a Redis storage action by setting the MonoBank integration token.

        Args:
            message (types.Message): The Telegram message associated with the action.
            token (str): The MonoBank integration token to be stored.

        Returns:
            bool: True if the token is successfully stored, False otherwise.
        """

        status = await RedisStorage().set(f"mono_auth_{message.chat.id}", token)

        if status:
            return True

        await bot.send_message(
            chat_id=message.chat.id,
            text=await Lang.get("update_mono_token_error", message)
        )

        return False

    @staticmethod
    @async_timer
    async def _msg_action(message: types.Message, client_fullname: str) -> None:
        """
        Performs a Telegram message action by deleting a specified message and sending a new message.

        Args:
            message (types.Message): The Telegram message associated with the action.
            client_fullname (str): The full name of the MonoBank client for the new message.
        """

        client_name = client_fullname.split()[-1]

        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=message.message_id
        )

        await bot.send_message(
            chat_id=message.chat.id,
            text=await Lang.get("mono_token_active", message) % client_name,
            reply_markup=await RollIn.session_buttons(message)
        )

    async def process(self) -> bool:
        """
        Initiates the token checking and refreshing process, updating the authentication token if necessary.

        Returns:
            bool: True if the token is successfully checked and refreshed, False otherwise.
        """

        await bot.send_chat_action(self.message.chat.id, types.ChatActions.TYPING)

        start_token = await self.get_start_token()
        token = await Mono().check_token(start_token)

        if not token:
            return False

        client = await Mono().client_info(self.message, token)
        message = self.message

        await self._redis_action(message, token)
        await self._msg_action(message, client.name)

        return True
