'''
    Pydentic schemas
'''
from pydantic import BaseModel, EmailStr, conint
from datetime import datetime
from typing import Optional

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True

# Post schemas
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True

class Post(PostBase):
    id: int
    created_at: datetime
    user_id: int
    user: User

    class Config:
        orm_mode = True

class PostVote(BaseModel):
    Post: Post
    votes: int
    
# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

# Vote schema
class Vote(BaseModel):
    post_id: int
    dir: conint(le=1) # ensure that dir is always <= 1