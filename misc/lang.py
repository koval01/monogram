import json
import logging
from aiogram import types


class Lang:
    dictionary: dict = {}
    default_lang: str = "en"
    
    def __init__(self) -> None:
        self.file: str = "lang.json"
        
    def load(self) -> None:
        Lang.dictionary = json.loads(open(self.file, "r").read())
        logging.info("Language data loaded")
        
    @classmethod
    def get(cls, key: str, message: types.Message) -> str:
        try:
            return cls.dictionary[key][message.from_user.language_code]
        except KeyError:
            return cls.dictionary[key][cls.default_lang]
        
