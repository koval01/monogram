import sys

from aiogram import types

from misc.mono import Mono


class CheckProto:
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
        
    async def process(self) -> types.Message:
        resp = await Mono().check_proto()
        return await self.message.reply(f"<code>{resp.model_dump_json()}</code>")


class Sys:

    def __init__(self, message: types.Message) -> None:
        self.message = message

    async def process(self) -> types.Message:
        return await self.message.reply(f"<code>{sys.version}</code>")
