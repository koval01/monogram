from aiogram import types
from aiohttp import ClientSession

from config import GA_ID, GA_SECRET

import logging as log


class Analytics:
    
    def __init__(self, message: types.Message, alt_action: str = None) -> None:
        self.id: str = GA_ID
        self.secret: str = GA_SECRET

        self.message = message
        self.alt_action = alt_action

        self.host = "www.google-analytics.com"
        self.path = "mp/collect"

    async def _request_to_ga_server(self, params: dict, json: dict) -> None:
        async with ClientSession() as session:
            try:
                async with session.post(
                    f"https://{self.host}/{self.path}", json=json, params=params
                ) as response:
                    if response.status >= 200 < 300:
                        log.debug("OK code Google Analytics")
                    else:
                        log.warning(f"Error code Google Analytics: {response.status}")
            except Exception as e:
                log.error("Error send request to Google Analytics. Details: %s" % e)

    @property
    def _payload(self) -> dict:
        """
        Build body for request to Google Analytics
        """
        user_id = self.message.from_user.id
        return {
            'client_id': str(user_id),
            'user_id': str(user_id),
            'events': ({
                'name': self.message.get_command()[1:]
                if not self.alt_action else self.alt_action,
                'params': {
                    'language': self.message.from_user.language_code,
                    'engagement_time_msec': '1',
                }
            },),
        }

    async def send(self) -> None:
        if not all((self.id, self.secret,)):
            return
        
        await self._request_to_ga_server({
            "measurement_id": self.id, "api_secret": self.secret
        }, self._payload)

    def __str__(self) -> str:
        return self.id
