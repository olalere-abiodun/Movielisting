from pydantic import BaseModel, ConfigDict, validator
from datetime import datetime, date
from typing import Optional
from decimal import Decimal, ROUND_HALF_UP

class UserBase(BaseModel):
    user_id : int
    username: str
    password: str
    email: str

class User(BaseModel):
    user_id : int
    username: str

    model_config = ConfigDict(from_attributes=True)

    
class UserCreate(BaseModel):
    full_name: str
    username: str
    password: str
    email: str

class UserResponse(BaseModel):
    username: str
    email: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(UserCreate):
    pass

class PasswordReset(BaseModel):
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class MovieBase(BaseModel):
    title: str
    genre: str
    description: str
    release_date: date

class Movie(MovieBase):
    movie_id : int
    
    model_config = ConfigDict(from_attributes=True)

class MovieUpload(MovieBase):
    pass

class MovieResponse(BaseModel):
    movie_id: int
    title: str
    genre: str
    description: str
    release_date: Optional[date] = None


    model_config = ConfigDict(from_attributes=True)

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    updated_at: Optional[date] = None


class RatingCreate(BaseModel):
    movie_title: str
    rating: int
    created_at: date

class RatingResponse(BaseModel):
    title: str
    rating: Decimal

    @validator('rating', pre=True, always=True)
    def round_rating(cls, value):
        if isinstance(value, (float, str)):
            value = Decimal(value)
        return value.quantize(Decimal('0.0'), rounding=ROUND_HALF_UP)


    model_config = ConfigDict(from_attributes=True)


class CommentBase(BaseModel):
    parent_comment_id : int
    user_id: int
    movie_id: int
    content: str
    created_at: datetime
    updated_at: datetime

class PostComment(BaseModel):
    content: str
    created_at: date

    model_config = ConfigDict(from_attributes=True)

class ParentCommentResponse(BaseModel):
    username: str
    movie_title: str
    content: str

    model_config = ConfigDict(from_attributes=True)

class CommentReplyBase(BaseModel):
    parent_comment_id : int
    user_id: int
    movie_id: int
    content: str
    created_at: datetime

class PostReply(BaseModel):
    content: str
    

class CommentReplyResponse(BaseModel):
    reply_id: int
    user_id: int
    parent_comment_id: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)