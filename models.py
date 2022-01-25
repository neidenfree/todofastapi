from typing import List

from bson import ObjectId
from pydantic import BaseModel, EmailStr
from connections import db


class User(BaseModel):
    username: str
    password: str
    email: EmailStr


class DBUser(User):
    id: str


class UserPasswordChange(User):
    new_password: str


class Response(BaseModel):
    ok: str
    messages: List[str]
