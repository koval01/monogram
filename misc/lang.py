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
        """
        Initializes a Lang instance with the default language file.
        """

        self.file: str = "lang.json"
        
    @staticmethod
    def __check_keys(a_keys: list, b_keys: list) -> bool:
        """
        Validates the sequence of keys to maintain cleanliness in JSON.

        Args:
            a_keys (list): First sequence of keys.
            b_keys (list): Second sequence of keys.

        Returns:
            bool: True if the sequences match, False otherwise.
        """
        
        # if len(a_keys) != len(b_keys):
        #     return False

        for key_1, key_2 in zip(a_keys, b_keys):
            if key_1 != key_2:
                return False

        return True

    @property
    def valid(self) -> bool:
        """
        Validates the loaded language data against expected structure.

        Returns:
            bool: True if the loaded data is valid, False otherwise.
        """

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
        """
        Loads language data from the specified JSON file.
        Raises an exception if the loaded data is not valid.
        """

        Lang.dictionary = json.loads(open(self.file, "r").read())
        if not self.valid:
            raise Exception("Error validate language data")

        logging.info("Language data loaded")

    @classmethod
    def lang_check(cls, message: types.Message) -> bool:
        """
        Checks if the user's language is valid based on language data.

        Args:
            message (types.Message): The Telegram message.

        Returns:
            bool: True if the user's language is valid, False otherwise.
        """

        if message.from_user.is_bot:
            return True
        
        return message.from_user.language_code in cls.dictionary["valid_lang_keys"]

    @staticmethod
    async def storage(usr_id: int, lang_code: str = None) -> str | None:
        """
        Manages user language preferences in Redis storage.

        Args:
            usr_id (int): User ID.
            lang_code (str): Language code.

        Returns:
            str | None: If lang_code is provided, returns None. Otherwise, returns the stored language code.
        """

        key = f"usr_lang_{usr_id}"
        if lang_code:
            await RedisStorage().set(key, lang_code)
        else:
            return await RedisStorage().get(key)

    @classmethod
    async def _get(cls, message: types.Message or types.CallbackQuery, code: str = None) -> str:
        """
        Gets the language code based on the user and message context.

        Args:
            message (types.Message or types.CallbackQuery): The Telegram message or callback query.
            code (str): Optional language code.

        Returns:
            str: The language code.
        """

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
        """
        Gets the translated message for a specific key based on the user's language.

        Args:
            key (str): The language key for the desired message.
            message (types.Message or types.CallbackQuery): The Telegram message or callback query.
            code (str): Optional language code.

        Returns:
            str: The translated message.
        """
        
        try:
            return cls.dictionary["keys"][key][await cls._get(message, code)]
        except (KeyError, AttributeError):
            return cls.dictionary["keys"][key][cls.default_lang]
        
