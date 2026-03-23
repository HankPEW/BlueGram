from datetime import datetime

from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import Integer, DateTime, String, ForeignKey, func

from src.models.base import Base


class Post(Base):
    __tablename__ = "posts"

    post_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.user_id", ondelete="CASCADE"),
        nullable=False
    )
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    body: Mapped[str] = mapped_column(String(1024), nullable=False)
    likes_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    user: Mapped["AuthUser"] = relationship("AuthUser", back_populates="posts")
    comments: Mapped[list["PostComment"]] = relationship(
        "PostComment",
        back_populates="post",
        cascade="all, delete-orphan"
    )
    likes: Mapped[list["PostLike"]] = relationship(
        "PostLike",
        back_populates="post",
        cascade="all, delete-orphan"
    )


class PostLike(Base):
    __tablename__ = "post_likes"

    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.post_id", ondelete="CASCADE"),
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

    post: Mapped[Post] = relationship(
        "Post",
        back_populates="likes"
    )

    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        back_populates="post_likes"
    )
