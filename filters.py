from aiogram import types
from aiogram.dispatcher.filters import BoundFilter
import config


class IsOwnerFilter(BoundFilter):
    """
    Custom filter "is_owner" for checking if the message sender is the bot owner.

    Args:
        is_owner (bool): A boolean indicating whether the message sender should be the bot owner.

    Usage:
    @dp.message_handler(IsOwnerFilter(is_owner=True), commands="admin_command")
    async def admin_command_handler(message: types.Message):
        # Your handler code here

    This filter can be applied to message handlers using the "is_owner" parameter.
    It checks whether the user who sent the message is one of the bot owners defined in the configuration.

    """
    
    key = "is_owner"

    def __init__(self, is_owner):
        self.is_owner = is_owner

    async def check(self, message: types.Message):
        return message.from_user.id in config.BOT_OWNERS
