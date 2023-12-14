from __future__ import annotations
from typing import Annotated

from pydantic import BaseModel, BeforeValidator


def coerce_str_to_bytes(data: str) -> bytes | any:
    if isinstance(data, str):
        return data.encode("utf-8")
    return data 


CoercedData = Annotated[bytes, BeforeValidator(coerce_str_to_bytes)]


class Model(BaseModel):
    token: str
    requestId: str
    url: str
    qr: CoercedData
    