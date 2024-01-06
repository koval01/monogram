import sys
import json

from time import time

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
        """
        Initializes a CheckProto instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the protocol checking process.
        """

        self.message = message
        
    async def process(self) -> types.Message:
        """
        Initiates the process of checking the MonoBank integration protocol and sends the result as a message.

        Returns:
            types.Message: The message containing the result of the protocol check.
        """

        resp = await Mono().check_proto()
        return await self.message.reply(f"<code>{resp.model_dump_json()}</code>")


class Sys:

    def __init__(self, message: types.Message) -> None:
        """
        Initializes a Sys instance with the given Telegram message.

        Args:
            message (types.Message): The Telegram message triggering the system information retrieval.
        """

        self.message = message

    @property
    def sys_info(self) -> str:
        """
        Retrieves and formats system information into a JSON string.

        Returns:
            str: The JSON-formatted string containing instance time, interpreter version, and package versions.
        """

        return json.dumps({
            "instance": {
                "time": int(time()),
                "interpreter": sys.version
            },
            "packages": {
                "aiogram": aiogram.__version__,
                "aiohttp": aiohttp.__version__,
                "redis": redis.__version__,
                "Pillow": PIL.__version__,
                "uvloop": uvloop.__version__,
                "ujson": ujson.__version__,
                "pydantic": pydantic.__version__
            }
        })

    async def process(self) -> types.Message:
        """
        Initiates the process of gathering and displaying system information as a message.

        Returns:
            types.Message: The message containing the formatted system information.
        """

        return await self.message.reply(f"<code>{self.sys_info}</code>")
