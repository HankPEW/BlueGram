from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


class UserProfile(Base):
    """Модель профиля пользователя."""

    __tablename__ = "users_profiles"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.user_id", ondelete="CASCADE"),
        primary_key=True
    )
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    gender: Mapped[str] = mapped_column(String(6), nullable=False)
    birth: Mapped[date] = mapped_column(Date, nullable=False)
    career: Mapped[str] = mapped_column(String(30))
    education: Mapped[str] = mapped_column(String(30))
    phone_number: Mapped[str] = mapped_column(String(15))
    marital_status: Mapped[str] = mapped_column(String(20))
    hometown: Mapped[str] = mapped_column(String(30))
    about_me: Mapped[str] = mapped_column(String(50))

    user: Mapped["AuthUser"] = relationship(
        "AuthUser",
        back_populates="profile"
    )
