from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class Post(BaseModel):
    name: str
    surname: str
    rating: Optional[int] = None


class CreatePost(Post):
    pass


class GetRes(BaseModel):
    name: str
    surname: str

    class Config:
        orm_mode = True


class PostRes(BaseModel):
    id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str


class PostedUser(BaseModel):
    email: EmailStr
    id: int
    created_at: datetime
