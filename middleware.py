import asyncio

from aiogram import types, Dispatcher

from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled

from misc.analytics import Analytics

from misc.lang import Lang


class ThrottlingMiddleware(BaseMiddleware):
    """
    Middleware for handling rate limiting/throttling
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_') -> None:
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process(self, message: types.Message | types.CallbackQuery) -> None:
        handler = current_handler.get()

        dispatcher = Dispatcher.get_current()
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            await self._throttled(message, t)
            raise CancelHandler()

    @staticmethod
    async def _throttled(message: types.Message | types.CallbackQuery, throttled: Throttled) -> None:
        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            if type(message) is types.CallbackQuery:
                query = message
                await query.answer(Lang.get("ratelimit", query.message), show_alert=True)
            else:
                await message.reply(Lang.get("ratelimit", message))

        await asyncio.sleep(delta)

    async def on_process_message(self, message: types.Message, _: any = None) -> None:
        await self.on_process(message)

    async def on_process_callback_query(self, query: types.CallbackQuery, _: any = None) -> None:
        await self.on_process(query)


class AnalyticsMiddleware(BaseMiddleware):
    def __init__(self):
        super(AnalyticsMiddleware, self).__init__()

    @staticmethod
    async def _send(message: types.Message) -> None:
        handler = current_handler.get()
        await Analytics(message=message, alt_action=handler.__name__).send()

    async def on_process_message(self, message: types.Message, _: any = None) -> None:
        await self._send(message)

    async def on_process_callback_query(self, query: types.CallbackQuery, _: any = None) -> None:
        await self._send(query.message)
