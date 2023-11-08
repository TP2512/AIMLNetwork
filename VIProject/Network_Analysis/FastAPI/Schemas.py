from typing import Optional
from pydantic import BaseModel

class Post(BaseModel):
    name : str
    surname : str
    rating : Optional[int] = None

class CreatePost(Post):
    pass
