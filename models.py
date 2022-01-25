from typing import List

from pydantic import BaseModel, EmailStr
from connections import db


class User(BaseModel):
    username: str
    password: str
    email: EmailStr


class Response(BaseModel):
    ok: str
    messages: List[str]
