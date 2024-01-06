import sys
import json

import pydantic
import redis
import PIL

import uvloop
import ujson

import aiohttp
import aiogram
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

    @property
    def sys_info(self) -> str:
        return json.dumps({
            "interpreter": sys.version,
            "aiogram": aiogram.__version__,
            "aiohttp": aiohttp.__version__,
            "redis": redis.__version__,
            "Pillow": PIL.__version__,
            "uvloop": uvloop.__version__,
            "ujson": ujson.__version__,
            "pydantic": pydantic.__version__
        })

    async def process(self) -> types.Message:
        return await self.message.reply(f"<code>{self.sys_info}</code>")
