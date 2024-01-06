import asyncio
import aiohttp

from aiogram import types
from aiohttp import ClientResponse

from misc import models

from misc.other import Other

from decorators import async_timer


class MonoAPI:
    """Written specifically for Sominemo implementation"""
    
    def __init__(self) -> None:
        """
        Initializes a MonoAPI instance with default host and origin.
        """

        self.host: str = "api.mono.sominemo.com"
        self.origin: str = "monoweb.app"
    
    async def request(self, api_method: str, method: str = "GET", data: dict = None, token: str = "") -> \
            ClientResponse.text or ClientResponse.json or None:
        """
        Makes an asynchronous request to the Mono API.

        Args:
            api_method (str): The specific API method to be called.
            method (str): The HTTP method for the request (default is "GET").
            data (dict): The data to be sent with the request (default is None).
            token (str): The token to be included in the request headers (default is "").

        Returns:
            ClientResponse.text or ClientResponse.json or None: The response body if successful, None otherwise.
        """
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(method, url=f'https://{self.host}/{api_method}', headers={
                    "Origin": f"https://{self.origin}",
                    "Referer": f"https://{self.origin}/",
                    "X-Request-Id": token
                }, data=data) as response:
                    body = await response.json() \
                           if response.headers.get("content-type").split(";")[0] == "application/json" \
                           else await response.text()
                    return body if response.status == 200 else None
            except (asyncio.TimeoutError, TypeError):
                return {"error": None}
            
    async def check_proto(self) -> dict | None:
        """
        Sends a request to check the Mono API protocol and returns the response.

        Returns:
            dict | None: The response body if successful, None otherwise.
        """

        body = await self.request("check-proto")
        return body
    
    async def roll_in(self) -> dict | None:
        """
        Sends a request to initiate the roll-in process and returns the response.

        Returns:
            dict | None: The response body if successful, None otherwise.
        """

        body = await self.request("roll-in")
        return body
    
    async def exchange_token(self, token: str) -> dict | None:
        """
        Sends a request to exchange a token and returns the response.

        Args:
            token (str): The token to be exchanged.

        Returns:
            dict | None: The response body if successful, None otherwise.
        """

        body = await self.request(
            "exchange-token", "POST", data={
                "token": token
            }
        )
        return body

    async def client_info(self, token: str) -> dict | None:
        """
        Sends a request to retrieve client information and returns the response.

        Args:
            token (str): The token for client information retrieval.

        Returns:
            dict | None: The response body if successful, None otherwise.
        """

        body = await self.request(
            "request/personal/client-info", "GET", token=token
        )
        return body


class Mono:
    
    @staticmethod
    @async_timer
    async def check_token(token: str) -> str | None:
        """
        Asynchronously checks the validity of a token by exchanging it with the Mono API.

        Args:
            token (str): The token to be checked.

        Returns:
            str | None: The validated token if successful, None otherwise.
        """

        data = await MonoAPI().exchange_token(token)
        model = models.exchange_token.Model(**data)
        return model.token if model.token else None
    
    @staticmethod
    @async_timer
    async def check_proto() -> models.check_proto.Model:
        """
        Asynchronously checks the Mono API protocol and returns the result as a check_proto model.

        Returns:
            models.check_proto.Model: The result of the protocol check.
        """

        data = await MonoAPI().check_proto()
        return models.check_proto.Model(**data)
    
    @staticmethod
    @async_timer
    async def roll_in() -> models.roll_in.Model:
        """
        Asynchronously initiates the roll-in process and returns the result as a roll_in model.

        Returns:
            models.roll_in.Model: The result of the roll-in process.
        """

        data = await MonoAPI().roll_in()
        return models.roll_in.Model(**data)

    @staticmethod
    @async_timer
    async def client_info(message: types.Message, token: str) -> models.client_info.Model:
        """
        Asynchronously retrieves client information using the provided token and returns the result
        as a client_info model.

        Args:
            message (types.Message): The message object for language translation.
            token (str): The token for client information retrieval.

        Returns:
            models.client_info.Model: The retrieved client information.
        """
        
        data = await MonoAPI().client_info(token)
        model = models.client_info.Model(**data)
        model.name = Other.name_translate(message.from_user.language_code, model.name)
        return model
