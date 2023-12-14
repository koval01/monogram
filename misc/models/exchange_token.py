from __future__ import annotations

from pydantic import BaseModel


class Model(BaseModel):
    token: bool | str = None
    error: str = None
