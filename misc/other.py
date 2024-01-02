from transliterate import translit


class Other:
    
    @staticmethod
    def name_translate(lang: str, name: str) -> str:
        if lang in ("uk", "ru",):
            return {
                "uk": name,
                "ru": name.lower().replace("і", "и").title()
            }[lang]

        return translit(name, 'uk', reversed=True)

    @staticmethod
    def format_number(number: int | float) -> str:
        return '{:,}'.format(number).replace(',', ' ')
