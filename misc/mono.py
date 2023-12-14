import asyncio
import aiohttp
from aiohttp import ClientResponse
from misc import models


class MonoAPI:
    """Written specifically for Sominemo implementation"""
    
    def __init__(self) -> None:
        self.host: str = "api.mono.sominemo.com"
        self.origin: str = "monoweb.app"
    
    async def request(self, api_method: str, method: str = "GET", data: dict = None, token: str = "") -> \
            ClientResponse.text or ClientResponse.json or None:
        
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
            except asyncio.TimeoutError:
                return {"error": None}
            
    async def check_proto(self) -> dict | None:
        body = await self.request("check-proto")
        return body
    
    async def roll_in(self) -> dict | None:
        body = await self.request("roll-in")
        return body
    
    async def exchange_token(self, token: str) -> dict | None:
        body = await self.request(
            "exchange-token", "POST", data={
                "token": token
            }
        )
        return body

    async def client_info(self, token: str) -> dict | None:
        body = await self.request(
            "request/personal/client-info", "GET", token=token
        )
        return body


class Mono:
    
    @staticmethod
    async def check_token(token: str) -> str | None:
        data = await MonoAPI().exchange_token(token)
        model = models.exchange_token.Model(**data)
        return model.token if model.token else None
    
    @staticmethod
    async def check_proto() -> models.check_proto.Model:
        data = await MonoAPI().check_proto()
        return models.check_proto.Model(**data)
    
    @staticmethod
    async def roll_in() -> models.roll_in.Model:
        data = await MonoAPI().roll_in()
        return models.roll_in.Model(**data)

    @staticmethod
    async def client_info(token: str) -> models.client_info.Model:
        data = await MonoAPI().client_info(token)
        return models.client_info.Model(**data)
