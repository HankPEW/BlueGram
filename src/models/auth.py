from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class AuthUser(Base):
    """Модель пользователя для аутентификации."""

    __tablename__ = "auth_users"

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    login: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        index=True
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    profile: Mapped["UserProfile"] = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )

    posts: Mapped[list["Post"]] = relationship(
        "Post",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    post_likes: Mapped[list["PostLike"]] = relationship(
        "PostLike",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    comments: Mapped[list["PostComment"]] = relationship(
        "PostComment",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    comment_likes: Mapped[list["CommentLike"]] = relationship(
        "CommentLike",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    refresh_tokens: Mapped[list["RefreshToken"]] = relationship(
        "RefreshToken",
        back_populates="auth_user",
        cascade="all, delete-orphan"
    )


class RefreshToken(Base):
    """Модель refresh токена пользователя."""

    __tablename__ = "refresh_tokens"

    token_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("auth_users.user_id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    auth_user: Mapped[AuthUser] = relationship(back_populates="refresh_tokens")
