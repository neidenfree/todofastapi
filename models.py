from typing import List

from bson import ObjectId
from pydantic import BaseModel, EmailStr
from connections import db


class User(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: str | None = None
    password: str
    email: EmailStr | None = None


class DBUser(User):
    id: str


class UserPasswordChange(User):
    new_password: str


class Response(BaseModel):
    ok: str
    messages: List[str]
