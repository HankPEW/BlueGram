import re
import string
from datetime import datetime
from typing import Annotated
from pydantic import BaseModel, Field


titleStr = Annotated[
    str,
    Field(
        min_length=2,
        max_length=50,
        pattern=rf"^[\w {re.escape(string.punctuation)}]+$"
    )
]


class PostBase(BaseModel):
    title: titleStr
    body: str = Field(min_length=2, max_length=1024)


class CreatePostRequest(PostBase):
    pass


class UpdatePostRequest(PostBase):
    title: titleStr | None = None
    body: str | None = Field(min_length=2, max_length=1024, default=None)


class ReadPostResponse(PostBase):
    id: int
    author: str
    created_at: datetime
    likes_count: int = Field(default=0)
    comments_count: int = Field(default=0)


class PostLikeResponse(BaseModel):
    user_id: int
    login: str
