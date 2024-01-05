from aiogram import types

from misc.mono import Mono

from decorators import async_timer


class CheckProto:
    
    def __init__(self, message: types.Message) -> None:
        self.message = message
        
    @async_timer
    async def process(self) -> types.Message:
        resp = await Mono().check_proto()
        return await self.message.reply(f"<code>{resp.model_dump_json()}</code>")
