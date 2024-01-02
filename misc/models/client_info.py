from __future__ import annotations
from typing import Annotated, Literal

from typing import List

from pydantic import BaseModel, BeforeValidator


def seperate_float(value: int) -> float:
    if isinstance(value, int):
        return float("{:.2f}".format(value / 100.0))
    return value


def currency_detect(value: int) -> str | any:
    if isinstance(value, int):
        return {980: "UAH", 978: "EUR", 840: "USD"}[value]
    return value


SeperateFloat = Annotated[float, BeforeValidator(seperate_float)]
CurrencyDetect = Annotated[str, BeforeValidator(currency_detect)]


class Account(BaseModel):
    id: str
    sendId: str
    currencyCode: CurrencyDetect
    cashbackType: str
    balance: SeperateFloat
    creditLimit: SeperateFloat
    maskedPan: List[str]
    type: Literal["black", "white", "platinum", "iron", "fop", "yellow", "eAid"]
    iban: str


class Model(BaseModel):
    clientId: str
    name: str
    webHookUrl: str
    permissions: str
    accounts: List[Account]
    