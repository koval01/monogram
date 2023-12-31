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

    async def on_process_message(self, message: types.Message, _: any = None) -> None:
        """
        Enforce rate limiting on message processing.

        Parameters:
        - message (types.Message): The incoming message.
        - _: (any): Placeholder for an unused parameter.
        """
        
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.message_throttled(message, t)

            # Cancel current handler
            raise CancelHandler()

    async def on_process_callback_query(self, query: types.CallbackQuery, _: any = None) -> None:
        """
        Enforce rate limiting on callback query processing.

        Parameters:
        - query (types.CallbackQuery): The incoming callback query.
        - _: (any): Placeholder for an unused parameter.
        """
        
        # Get current handler
        handler = current_handler.get()

        # Get dispatcher from context
        dispatcher = Dispatcher.get_current()
        # If handler was configured, get rate limit and key from handler
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key', f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Use Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Execute action
            await self.callback_query_throttled(query, t)

            # Cancel current handler
            raise CancelHandler()

    @staticmethod
    async def message_throttled(message: types.Message, throttled: Throttled) -> None:
        """
        Notify the user about rate limiting when the rate is exceeded for messages.

        Parameters:
        - message (types.Message): The message that triggered rate limiting.
        - throttled (Throttled): Throttled instance containing rate limiting information.
        """

        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta

        # Prevent flooding
        if throttled.exceeded_count <= 2:
            await message.reply(Lang.get("ratelimit", message))

        # Sleep.
        await asyncio.sleep(delta)

    @staticmethod
    async def callback_query_throttled(query: types.CallbackQuery, throttled: Throttled) -> types.CallbackQuery:
        """
        Notify the user about rate limiting when the rate is exceeded for callback queries.

        Parameters:
        - query (types.CallbackQuery): The callback query that triggered rate limiting.
        - throttled (Throttled): Throttled instance containing rate limiting information.
        """
        
        # Calculate how many time is left till the block ends
        delta = throttled.rate - throttled.delta

        if throttled.exceeded_count <= 2:
            return await query.answer(Lang.get("ratelimit", query.message), show_alert=True)

        # Sleep.
        await asyncio.sleep(delta)


class AnalyticsMiddleware(BaseMiddleware):
    def __init__(self):
        super(AnalyticsMiddleware, self).__init__()

    @staticmethod
    async def on_process_message(message: types.Message, _):
        handler = current_handler.get()
        await Analytics(message=message, alt_action=handler.__name__).send()

    @staticmethod
    async def on_process_callback_query(query: types.CallbackQuery, _: any = None) -> None:
        handler = current_handler.get()
        await Analytics(message=query.message, alt_action=handler.__name__).send()
