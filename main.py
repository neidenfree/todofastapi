import json
from typing import List, Any, Optional

from fastapi import FastAPI
from pymongo import MongoClient

from pydantic import BaseModel, EmailStr

app = FastAPI()
client = MongoClient('mongodb://localhost:27017/')
db = client.newBase


class UserIn(BaseModel):
    username: str
    password: str
    email: EmailStr
    full_name: str | None = None


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserInDB(BaseModel):
    username: str
    hashed_password: str
    email: EmailStr
    full_name: str | None = None


class UserLogin(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

    hashed_password: str

    def in_db(self):
        users = db.users
        a = users.find_one(dict(self))
        print(a)
        return a is not None


def password_hasher(raw_password: str):
    return "secret" + raw_password


def save_user(user_in: UserIn):
    hashed_password = password_hasher(user_in.password)
    collection = db.users
    user_in_db = UserInDB(**user_in.dict(), hashed_password=hashed_password)
    collection.insert_one(user_in_db.dict())
    return user_in_db


@app.post("/user/", response_model=UserOut)
async def create_user(user_in: UserIn):
    user_saved = save_user(user_in)
    return user_saved


@app.post("/login")
async def login(user: UserLogin):
    """Возможно, нужно будет сделать сессии"""
    user.hashed_password = password_hasher(user.hashed_password)
    if user.in_db():
        return 'ok'
    return 'no user like this'


