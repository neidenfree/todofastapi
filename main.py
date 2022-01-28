import asyncio
from bson import ObjectId

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from connections import users, tasks
from models import *

from utils import password_hash

app = FastAPI()
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",

]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


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


def save_user(user_in: User) -> dict:
    a = users.find_one({"$or":
                            [{"username": user_in.username},
                             {"email": user_in.email}]
                        }, {})
    if a is not None:
        return {"ok": False, "message": "There are user with this username or email! Please, choose another username or email!"}
    user_in.password = password_hash(user_in.password)
    users.insert_one(dict(user_in))
    return {"ok": True, "username": user_in.username, "email": user_in.email}


@app.post("/register/")
async def create_user(user_in: User) -> dict:
    print("START")
    result = save_user(user_in)
    return result


@app.post("/login/", response_model=DBUser)
async def login(user: UserLogin) -> DBUser:
    # Just to make this process longer
    await asyncio.sleep(0.5)
    db_user = get_user_or_none(user)
    if not db_user:
        raise HTTPException(status_code=401, detail="No user with such login data")
    return db_user


@app.put("/change-password")
async def change_password(user: UserPasswordChange):
    """Password match check must be on a frontend side"""
    print(user)
    # return {'ok': True, 'message': "Password changed successfully!"}
    if not (us := get_user_or_none(user)):
        return {'ok': False, 'message': "Password or username is invalid!"}
    print(user)
    a = users.find_one({'_id': ObjectId(us.id)})
    print('a = ', a)
    users.update_one({'_id': ObjectId(us.id)}, {
        '$set': {'password': password_hash(user.new_password)}
    }, upsert=False)


@app.get("/get-all")
def get_all_users():
    res = users.find({}, {"_id": 0})
    result = []
    for elem in res:
        result.append(elem)
    return result


@app.post("/tasks")
def get_user_tasks(user: UserLogin):
    db_user = get_user_or_none(user)
    user_tasks = tasks.find({'user_id': ObjectId(db_user.id)})
    print('db_user = ', db_user)
    result = []
    for task in user_tasks:
        print('task = ', task)
        task["user_id"] = str(task["user_id"])
        task["task_id"] = str(task["_id"])
        task_model = Task(**task)
        # task = str(task.task_id)
        # task.user_id = str(task.user_id)
        result.append(task_model)
    print('result = ', result)

    return result


# @app.post("/tasks", response_model=Task)
@app.post("/tasks/new")
async def add_task(user: UserLogin, task: Task):
    """
    One of the cool things about MongoDB is that the ids are generated client side.

    This means you don't even have to ask the server what the id was, because you told it
        what to save in the first place. Using pymongo the return value of an insert will be the object id.
    """
    db_user = get_user_or_none(user)
    if db_user is None:
        return "Wrong user!"
    task.user_id = ObjectId(db_user.id)
    inserted_task = tasks.insert_one(dict(task))
    task.user_id = str(task.user_id)
    task.task_id = str(inserted_task.inserted_id)
    return task


@app.delete("/task")
async def delete_task(user_delete: DeleteTaskUserLogin):
    db_user = get_user_or_none(user_delete)
    if not db_user:
        return "not okay"
    try:
        a = tasks.delete_one({"user_id": ObjectId(db_user.id), "_id": ObjectId(user_delete.task_id)})
        if a.deleted_count == 0:
            return "no delete"
        return "ok"
    except:
        return "not okay"


@app.put("/task")
async def modify_task(user: UserLogin, task: Task):
    db_user = get_user_or_none(user)
    if db_user is None:
        return "Wrong user!"
    if task.task_id is None:
        return "Wrong!"
    task.user_id = ObjectId(db_user.id)
    a = tasks.find_one({'_id': ObjectId(task.task_id)})
    if a is None:
        return "No such element"
    users.update_one({'_id': ObjectId(task.task_id)}, {
        '$set': {'description': task.description, "title": task.title, "done": task.done}
    }, upsert=False)
