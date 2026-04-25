from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class PostComment(Base):
    """Модель комментария к посту."""

    __tablename__ = "post_comments"

    comment_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.post_id", ondelete="CASCADE"),
        nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    comment_text: Mapped[str] = mapped_column(String(1024), nullable=False)
    likes_count : Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
    likes: Mapped[list["CommentLike"]] = relationship(
        "CommentLike",
        back_populates="comment",
        cascade="all, delete-orphan"
    )
    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        back_populates="comments"
    )


class CommentLike(Base):
    """Модель лайка комментария."""

    __tablename__ = "comment_likes"

    comment_id: Mapped[int] = mapped_column(
        ForeignKey("post_comments.comment_id", ondelete="CASCADE"),
        primary_key=True
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    comment: Mapped[PostComment] = relationship(
        "PostComment",
        back_populates="likes"
    )
    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        back_populates="comment_likes"
    )
