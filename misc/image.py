import os
import base64

from typing import Literal

from PIL import Image, ImageFont, ImageDraw
from io import BytesIO


class ImageProcess:
    
    def __init__(self, file: str | bytes) -> None:
        self.path: str = os.path.join(os.getcwd(), "misc")
        
        if isinstance(file, bytes):
            file = BytesIO(base64.b64decode(file))
        else:
            file = os.path.join(self.path, "images", file)
            
        self.image = Image.open(file).convert('RGB')
        
    def add_text(
            self,
            text: str,
            pos: tuple,
            color: tuple = (255, 255, 255),
            font: str = "Montserrat-Regular.ttf",
            size: int = 16,
            align: Literal["left", "center", "right"] = "center"
    ) -> None:
        _, ph = pos
        draw = ImageDraw.Draw(self.image)
        font = ImageFont.truetype(os.path.join(self.path, "fonts", font), size)
        
        if align == "center":
            w, h = self.image.size
            _, _, w_tb, h_tb = draw.textbbox((0, 0), text, font=font)
            pos = ((w-w_tb)/2, ph)
            
        draw.text(pos, text, color, font=font, align=align)
        
    def __bytes__(self) -> bytes:
        buffered = BytesIO()
        self.image.save(buffered, format="JPEG", quality=75)
        
        return buffered.getvalue()[:]
