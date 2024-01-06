import re
import cyrtranslit


class Other:
    
    @staticmethod
    def name_translate(lang: str, name: str) -> str:
        """
        Translates the given name based on the specified language code.

        Args:
            lang (str): The language code.
            name (str): The name to be translated.

        Returns:
            str: The translated name.
        """

        if lang in ("uk", "ru",):
            return {
                "uk": name,
                "ru": name.lower().replace("і", "и").title()
            }[lang]

        return re.sub(r"[^a-zA-Z\s]+", "", cyrtranslit.to_latin(name, "ru").title())

    @staticmethod
    def format_number(number: int | float) -> str:
        """
        Formats the given number to a string with commas as thousand separators and two decimal places.

        Args:
            number (int | float): The number to be formatted.

        Returns:
            str: The formatted number as a string.
        """

        return '{:,.2f}'.format(number).replace(',', ' ')

    @staticmethod
    def identify_credit_card(card_number: int) -> str | None:
        """
        Identifies the type of credit card based on the provided card number.

        Args:
            card_number (int): The credit card number.

        Returns:
            str | None: The identified credit card type or None if not recognized.
        """
        
        card_number_str = str(card_number)

        card_patterns = {
            "VISA": r"^4[0-9]{12}(?:[0-9]{3})?$",
            "MASTERCARD": r"^5[1-5][0-9]{14}$"
        }

        for card_type, pattern in card_patterns.items():
            if re.match(pattern, card_number_str):
                return card_type
