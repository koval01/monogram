from __future__ import annotations

from pydantic import BaseModel


class Proto(BaseModel):
    version: int
    patch: int


class Implementation(BaseModel):
    name: str
    author: str
    homepage: str


class Push(BaseModel):
    api: str
    cert: str
    name: str


class Server(BaseModel):
    push: Push


class Model(BaseModel):
    proto: Proto
    implementation: Implementation
    server: Server
    