import base64

from misc.mono import Mono
from misc.lang import Lang

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class RollIn:
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
    
    def keyboard_create(self, url: str) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardMarkup()
        
        keyboard.add(InlineKeyboardButton(
            Lang.get("link_button", self.message), url=url))
        keyboard.add(InlineKeyboardButton(
            Lang.get("check_token_button", self.message), callback_data="check_token_button"))
        
        return keyboard
    
    async def process(self) -> types.Message:
        roll = await Mono().roll_in()
        
        if not roll:
            return await self.message.reply(Lang.get("roll_error", self.message))
        
        return await self.message.reply_photo(
            base64.decodebytes(roll.qr), Lang.get("start", self.message),
            reply_markup=self.keyboard_create(roll.url))
