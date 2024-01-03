import re
import cyrtranslit


class Other:
    
    @staticmethod
    def name_translate(lang: str, name: str) -> str:
        if lang in ("uk", "ru",):
            return {
                "uk": name,
                "ru": name.lower().replace("і", "и").title()
            }[lang]

        return re.sub(r"[^a-zA-Z\s]+", "", cyrtranslit.to_latin(name, "ru").title())

    @staticmethod
    def format_number(number: int | float) -> str:
        return '{:,.2f}'.format(number).replace(',', ' ')
