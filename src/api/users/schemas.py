from datetime import date, datetime
from typing import Annotated, Literal, Optional

from pydantic import AfterValidator, Field

from src.api.auth.schemas import (
    EmailStr,
    NameStr,
    PhoneStr,
    ProfileBase,
    birth_validator,
    login_validation,
)

class FullProfileBase(ProfileBase):
    """Базовая схема полного профиля пользователя с дополнительными полями."""
    career: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30
    )
    education: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30
    )
    phone_number: Optional[PhoneStr] = Field(default=None)
    marital_status: Optional[
        Literal[
            'single',
            'betrothed',
            'married',
            'single & looking',
            'in love',
            'got a girlfriend'
        ]
    ] = Field(default=None)
    hometown: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=30
    )
    about_me: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=50
    )


class ReadProfileResponse(FullProfileBase):
    """Схема ответа с данными профиля пользователя."""
    created_at: datetime


class UpdateProfileRequest(FullProfileBase):
    """Схема запроса для обновления профиля пользователя."""
    login: Optional[Annotated[str, AfterValidator(login_validation)]] = None
    email: Optional[EmailStr] = None
    first_name: Optional[NameStr] = None
    last_name: Optional[NameStr] = None
    gender: Optional[Literal["male", "female"]] = None
    birth: Optional[Annotated[date, AfterValidator(birth_validator)]] = None



