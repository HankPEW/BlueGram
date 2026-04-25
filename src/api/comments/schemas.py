from datetime import datetime

from pydantic import BaseModel, Field


class CommentBase(BaseModel):
    """Базовая схема комментария."""
    comment_text: str = Field(min_length=2, max_length=1024)


class CreateCommentRequest(CommentBase):
    """Схема запроса на создание комментария."""
    pass


class UpdateCommentRequest(CommentBase):
    """Схема запроса на обновление комментария."""
    comment_text: str | None = Field(min_length=2, max_length=1024, default=None)


class ReadCommentResponse(CommentBase):
    """Схема ответа с данными комментария."""
    id: int
    author: str
    created_at: datetime
    likes_count: int


class CommentLikeResponse(BaseModel):
    """Схема ответа с информацией о лайке комментария."""
    user_id: int
    login: str
