import os
import base64

from typing import Literal

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class ImageProcess:
    
    def __init__(self, file: str | bytes) -> None:
        """
        Initializes an ImageProcess instance with the given file path or bytes.

        Args:
            file (str | bytes): The file path or bytes of the image.
        """

        self.path: str = os.path.join(os.getcwd(), "misc")
        
        if isinstance(file, bytes):
            file = BytesIO(base64.b64decode(file))
        else:
            file = os.path.join(self.path, "images", file)
            
        self.image = Image.open(file).convert('RGBA')

    def perspective(self, mv: float) -> None:
        """
        Applies a perspective transformation to the image.

        Args:
            mv (float): The perspective transformation factor.
        """

        width, height = self.image.size

        xshift = mv * width
        new_width = width + int(round(abs(xshift)))

        transform_matrix = (1, mv, -xshift if mv > 0 else 0, 0, 1, 0)

        self.image = self.image.transform(
            (new_width, height),
            Image.AFFINE, transform_matrix, Image.BICUBIC
        )

    def add_text(
            self,
            text: str,
            pos: tuple,
            color: tuple = (255, 255, 255),
            font: str = "Montserrat-Regular.ttf",
            size: int = 16,
            align: Literal["left", "center", "right"] = "center"
    ) -> None:
        """
        Adds text to the image at the specified position with optional styling.

        Args:
            text (str): The text to be added.
            pos (tuple): The position (x, y) where the text will be placed.
            color (tuple, optional): The RGB color tuple. Defaults to (255, 255, 255).
            font (str, optional): The font file name. Defaults to "Montserrat-Regular.ttf".
            size (int, optional): The font size. Defaults to 16.
            align (Literal["left", "center", "right"], optional): The text alignment. Defaults to "center".
        """

        _, ph = pos
        draw = ImageDraw.Draw(self.image)
        font = ImageFont.truetype(os.path.join(self.path, "fonts", font), size)
        
        if align == "center":
            w, h = self.image.size
            _, _, w_tb, h_tb = draw.textbbox((0, 0), text, font=font)
            pos = ((w-w_tb)/2, ph)
            
        draw.text(pos, text, color, font=font, align=align)
        
    def __bytes__(self) -> bytes:
        """
        Converts the image to bytes.

        Returns:
            bytes: The image bytes.
        """
        
        buffered = BytesIO()
        self.image.save(buffered, format="PNG", quality=95)
        
        return buffered.getvalue()[:]
