from aiogram import types
from aiogram.types import InputTextMessageContent, InlineQueryResultArticle

from dispatcher import dp, bot

import hashlib


@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    text = inline_query.query or 'echo'
    input_content = InputTextMessageContent(text)
    result_id: str = hashlib.md5(text.encode()).hexdigest()
    item = InlineQueryResultArticle(
        id=result_id,
        title=f'Result {text!r}',
        input_message_content=input_content,
    )
    # don't forget to set cache_time=1 for testing (default is 300s or 5m)
    await bot.answer_inline_query(inline_query.id, results=[item], cache_time=1)

