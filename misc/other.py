from transliterate import translit


class Other:
    
    @staticmethod
    def name_translate(lang: str, name: str) -> str:
        if lang == "uk":
            return name
        return translit(name, 'uk', reversed=True)
