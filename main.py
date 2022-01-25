import asyncio
from bson import ObjectId

from fastapi import FastAPI
from connections import users, tasks
from models import *

from utils import password_hash

app = FastAPI()


def user_auth(user: UserLogin) -> bool:
    a = users.find_one(
        {"$and": [
            {"$or":
                 [{"username": user.username},
                  {"email": user.email}]
             },
            {"password": password_hash(user.password)}]
        })
    return a is not None


def get_user_or_none(user: UserLogin) -> Optional[DBUser]:
    a = users.find_one(
        {"$and": [
            {"$or":
                 [{"username": user.username},
                  {"email": user.email}]
             },
            {"password": password_hash(user.password)}]
        })
    print('a = ', a)
    if a is None:
        return None

    return DBUser(**a, id=str(a['_id']))


def save_user(user_in: User) -> str:
    a = users.find_one({"$or":
                            [{"username": user_in.username},
                             {"email": user_in.email}]
                        }, {})
    print(a)
    if a is not None:
        return "There are user with this username or email!"
    user_in.password = password_hash(user_in.password)
    users.insert_one(dict(user_in))
    return "ok"


@app.post("/register/")
async def create_user(user_in: User) -> str:
    message = save_user(user_in)
    return message


@app.post("/login/")
async def login(user: UserLogin) -> str:
    # Just to make this process longer
    await asyncio.sleep(0.5)
    if not user_auth(user):
        return "no"
    return "yes"


@app.put("/change-password")
async def change_password(user: UserPasswordChange):
    """Password validation must be on a frontend side"""
    if not (us := get_user_or_none(user)):
        return "Wrong username and password!"
    print(user)
    a = users.find_one({'_id': ObjectId(us.id)})
    print('a = ', a)
    users.update_one({'_id': ObjectId(us.id)}, {
        '$set': {'password': password_hash(user.new_password)}
    }, upsert=False)


@app.get("/get-all")
def get_all_users():
    collection = db.users
    res = collection.find({}, {"_id": 0})
    result = []
    for elem in res:
        result.append(elem)
    return result


@app.get("/tasks")
def get_user_tasks(user: User):
    db_user = get_user_or_none(user)
    user_tasks = tasks.find({'user': ObjectId(db_user.id)})
    print(user_tasks)


# @app.post("/tasks", response_model=Task)
@app.post("/tasks")
async def add_task(user: UserLogin, task: Task):
    """
    One of the cool things about MongoDB is that the ids are generated client side.

    This means you don't even have to ask the server what the id was, because you told it
        what to save in the first place. Using pymongo the return value of an insert will be the object id.
    """
    db_user = get_user_or_none(user)
    print('db_user = ', db_user)
    if db_user is None:
        return "Wrong user!"
    print(task)
    task.user_id = ObjectId(db_user.id)
    inserted_task = tasks.insert_one(dict(task))
    task.user_id = str(task.user_id)
    task.task_id = str(inserted_task.inserted_id)

    return task
