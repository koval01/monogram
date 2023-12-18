import json
import logging
from aiogram import types


class Lang:
    dictionary: dict = {}
    default_lang: str = "en"
    
    def __init__(self) -> None:
        self.file: str = "lang.json"
        
    @property
    def valid(self) -> bool:
        for key in self.dictionary["keys"]:
            for l_key in self.dictionary["valid_lang_keys"]:
                if l_key not in self.dictionary["keys"][key].keys():
                    return False

        return True

    def load(self) -> None:
        Lang.dictionary = json.loads(open(self.file, "r").read())
        if not self.valid:
            raise Exception("Error validate language data")

        logging.info("Language data loaded")

    @classmethod
    def lang_check(cls, message: types.Message) -> bool:
        return message.from_user.language_code in cls.dictionary["valid_lang_keys"]

    @classmethod
    def get(cls, key: str, message: types.Message or any, code: str = None) -> str:
        try:
            return cls.dictionary["keys"][key][code if code else message.from_user.language_code]
        except (KeyError, AttributeError):
            return cls.dictionary["keys"][key][cls.default_lang]
        
