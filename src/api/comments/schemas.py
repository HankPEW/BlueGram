from datetime import datetime
from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    comment_text: str = Field(min_length=2, max_length=1024)


class CreateCommentRequest(CommentBase):
    pass


class UpdateCommentRequest(CommentBase):
    comment_text: str | None = Field(min_length=2, max_length=1024, default=None)


class ReadCommentResponse(CommentBase):
    id: int
    author: str
    created_at: datetime
    likes_count: int


class CommentLikeResponse(BaseModel):
    user_id: int
    login: str