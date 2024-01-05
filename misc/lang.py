import json
import logging

from aiogram import types

from decorators import async_timer

from misc.redis_storage import RedisStorage


class Lang:
    dictionary: dict = {}
    usr_langs: dict = {}
    default_lang: str = "en"
    
    def __init__(self) -> None:
        self.file: str = "lang.json"
        
    @staticmethod
    def __check_keys(a_keys: list, b_keys: list) -> bool:
        """Validation of sequence of keys to maintain cleanliness in json"""
        
        # if len(a_keys) != len(b_keys):
        #     return False

        for key_1, key_2 in zip(a_keys, b_keys):
            if key_1 != key_2:
                return False

        return True

    @property
    def valid(self) -> bool:
        valid_keys = self.dictionary["valid_lang_keys"]

        for key in self.dictionary["keys"]:
            for l_key in valid_keys:

                kl = self.dictionary["keys"][key].keys()
                if l_key not in kl:
                    return False

                for kl_key in kl:
                    if kl_key not in valid_keys:
                        return False

                if not self.__check_keys(kl, valid_keys):
                    return False

        return True

    def load(self) -> None:
        Lang.dictionary = json.loads(open(self.file, "r").read())
        if not self.valid:
            raise Exception("Error validate language data")

        logging.info("Language data loaded")

    @classmethod
    def lang_check(cls, message: types.Message) -> bool:
        if message.from_user.is_bot:
            return True
        
        return message.from_user.language_code in cls.dictionary["valid_lang_keys"]

    @staticmethod
    async def storage(usr_id: int, lang_code: str = None) -> str | None:
        key = f"usr_lang_{usr_id}"
        if lang_code:
            await RedisStorage().set(key, lang_code)
        else:
            return await RedisStorage().get(key)

    @classmethod
    async def _get(cls, message: types.Message or types.CallbackQuery, code: str = None) -> str:
        usr_id: int = 0
        if message.from_user:
            code = message.from_user.language_code
            usr_id = message.from_id if not message.from_user.is_bot else 0
        if message.reply_to_message:
            code = message.reply_to_message.from_user.language_code
            usr_id = message.reply_to_message.from_id if not message.reply_to_message.from_user.is_bot else 0
        if message.chat.type == "private":
            usr_id = message.chat.id

        if usr_id and code:
            cls.usr_langs[usr_id] = code
            await cls.storage(usr_id, code)

        if usr_id in cls.usr_langs:
            return cls.usr_langs[usr_id]

        storage = await cls.storage(usr_id)
        if storage:
            return storage

        return cls.default_lang

    @classmethod
    @async_timer
    async def get(cls, key: str, message: types.Message or types.CallbackQuery, code: str = None) -> str:
        try:
            return cls.dictionary["keys"][key][await cls._get(message, code)]
        except (KeyError, AttributeError):
            return cls.dictionary["keys"][key][cls.default_lang]
        
