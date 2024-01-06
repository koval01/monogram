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
    Middleware for handling rate limiting/throttling.

    Usage:
    # Add the middleware to your Dispatcher instance
    dp.middleware.setup(ThrottlingMiddleware())

    This middleware handles rate limiting or throttling of incoming messages and callback queries
    based on the specified rate limit for each handler.

    Attributes:
        rate_limit (int): Default rate limit in seconds.
        prefix (str): Prefix used to generate unique keys for rate limiting.

    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_') -> None:
        """
        Initialize the ThrottlingMiddleware.

        Args:
            limit (int): Default rate limit in seconds.
            key_prefix (str): Prefix used to generate unique keys for rate limiting.

        """

        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process(self, message: types.Message | types.CallbackQuery) -> None:
        """
        Middleware method called when processing incoming messages or callback queries.

        Args:
            message (types.Message | types.CallbackQuery): The incoming message or callback query.

        """

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
        """
        Handle the case when a message or callback query exceeds the rate limit.

        Args:
            message (types.Message | types.CallbackQuery): The incoming message or callback query.
            throttled (Throttled): Throttled instance with rate limit details.

        """

        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            if type(message) is types.CallbackQuery:
                query = message
                await query.answer(await Lang.get("ratelimit", query.message), show_alert=True)
            else:
                await message.reply(await Lang.get("ratelimit", message))

        await asyncio.sleep(delta)

    async def on_process_message(self, message: types.Message, _: any = None) -> None:
        """
        Middleware method called when processing incoming messages.

        Args:
            message (types.Message): The incoming message.
            _: (any): Unused parameter.

        """

        await self.on_process(message)

    async def on_process_callback_query(self, query: types.CallbackQuery, _: any = None) -> None:
        """
        Middleware method called when processing incoming callback queries.

        Args:
            query (types.CallbackQuery): The incoming callback query.
            _: (any): Unused parameter.

        """
        
        await self.on_process(query)


class AnalyticsMiddleware(BaseMiddleware):
    """
    Middleware for sending analytics data based on incoming messages and callback queries.

    Usage:
    # Add the middleware to your Dispatcher instance
    dp.middleware.setup(AnalyticsMiddleware())

    This middleware automatically sends analytics data to the configured analytics service
    when processing incoming messages and callback queries. The analytics event is determined
    by the name of the handler associated with the message or query.

    """

    def __init__(self):
        super(AnalyticsMiddleware, self).__init__()

    @staticmethod
    async def _send(message: types.Message) -> None:
        """
        Helper method to send analytics data for a given message.

        Args:
            message (types.Message): The incoming message.

        """

        handler = current_handler.get()
        await Analytics(message=message, alt_action=handler.__name__).send()

    async def on_process_message(self, message: types.Message, _: any = None) -> None:
        """
        Middleware method called when processing incoming messages.

        Args:
            message (types.Message): The incoming message.
            _: (any): Unused parameter.

        """

        await self._send(message)

    async def on_process_callback_query(self, query: types.CallbackQuery, _: any = None) -> None:
        """
        Middleware method called when processing incoming callback queries.

        Args:
            query (types.CallbackQuery): The incoming callback query.
            _: (any): Unused parameter.

        """

        await self._send(query.message)
