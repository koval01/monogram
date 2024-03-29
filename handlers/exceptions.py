import logging
from aiogram.utils.exceptions import (Unauthorized, InvalidQueryID, TelegramAPIError,
                                      CantDemoteChatCreator, MessageNotModified, MessageToDeleteNotFound,
                                      MessageTextIsEmpty, RetryAfter,
                                      CantParseEntities, MessageCantBeDeleted)

from dispatcher import dp, bot
from misc.lang import Lang


@dp.errors_handler()
async def errors_handler(update, exception) -> bool:
    """
    Exception handler for Aiogram errors.

    Args:
        update: The incoming update or callback_query triggering the error.
        exception: The exception that occurred.

    Returns:
        bool: True if the error is handled, False otherwise.
    """

    if update:
        try:
            update = update.callback_query
        except AttributeError:
            pass

        # Notify the user about the exception
        await bot.send_message(
            update.message.chat.id,
            await Lang.get("exception", update.message) % exception.__class__.__name__
        )

    # Handle specific exceptions
    if isinstance(exception, CantDemoteChatCreator):
        logging.debug("Can't demote chat creator")
        return True

    if isinstance(exception, MessageNotModified):
        logging.debug('Message is not modified')
        return True
    if isinstance(exception, MessageCantBeDeleted):
        logging.debug('Message cant be deleted')
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logging.debug('Message to delete not found')
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logging.debug('MessageTextIsEmpty')
        return True

    if isinstance(exception, Unauthorized):
        logging.info(f'Unauthorized: {exception}')
        return True

    if isinstance(exception, InvalidQueryID):
        logging.exception(f'InvalidQueryID: {exception} \nUpdate: {update}')
        return True

    if isinstance(exception, TelegramAPIError):
        logging.exception(f'TelegramAPIError: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, RetryAfter):
        logging.exception(f'RetryAfter: {exception} \nUpdate: {update}')
        return True
    if isinstance(exception, CantParseEntities):
        logging.exception(f'CantParseEntities: {exception} \nUpdate: {update}')
        return True

    # Log other exceptions for debugging purposes
    logging.exception(f'Update: {update} \n{exception}')
