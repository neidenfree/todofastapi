import json
from typing import List, Any, Optional

from fastapi import FastAPI
from connections import db
from models import *

app = FastAPI()


def password_hasher(raw_password: str):
    return "secret" + raw_password


def save_user(user_in: User) -> str:
    collection = db.users
    a = collection.find_one({"$or":
                                 [{"username": user_in.username},
                                  {"email": user_in.email}]
                             }, {})
    print(a)
    if a is not None:
        return "There are user with this username or email!"
    collection.insert_one(dict(user_in))
    return "ok"


@app.post("/register/")
async def create_user(user_in: User) -> str:
    print(user_in)
    message = save_user(user_in)
    return message


@app.post("/login/")
async def login(user: User) -> str:
    collection = db.users
    a = collection.find_one(
        {"$and": [
            {"$or":
                 [{"username": user.username},
                  {"email": user.email}]
             },
            {"password": user.password}]
        })

    if a is None:
        return "no"
    return "yes"


@app.get("/get-all")
def get_all_users():
    collection = db.users
    res = collection.find({}, {"_id": 0})
    result = []
    for elem in res:
        result.append(elem)
    return result
