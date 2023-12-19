import json
import logging
from aiogram import types


class Lang:
    dictionary: dict = {}
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
        return message.from_user.language_code in cls.dictionary["valid_lang_keys"]

    @classmethod
    def get(cls, key: str, message: types.Message or any, code: str = None) -> str:
        try:
            return cls.dictionary["keys"][key][code if code else message.from_user.language_code]
        except (KeyError, AttributeError):
            return cls.dictionary["keys"][key][cls.default_lang]
        
