from pydantic import BaseModel
from typing import List, Optional


class Blog(BaseModel):
    title: str
    body: str

    class Config():
        orm_mode = True


class User(BaseModel):
    username: str
    email: str
    password: str

    class Config():
        orm_mode = True


class ShowUser(BaseModel):
    username: str
    email: str
    blogs: List[Blog] = []

    class Config():
        orm_mode = True


class ShowUser2(BaseModel):
    username: str
    email: str

    class Config():
        orm_mode = True


class ShowBlog(BaseModel):
    title: str
    body: str
    creator: ShowUser2

    class Config():
        orm_mode = True


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


