from typing import List, Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    password: str
    email: EmailStr


class UserLogin(BaseModel):
    username: Optional[str]
    email: Optional[EmailStr]
    password: str


class DeleteTaskUserLogin(UserLogin):
    task_id: str


class DBUser(User):
    id: str


class UserPasswordChange(User):
    new_password: str


class Response(BaseModel):
    ok: bool
    message: str


class Task(BaseModel):
    user_id: Optional[str]
    task_id: Optional[str]
    title: str
    description: str | None = None
    done: bool
