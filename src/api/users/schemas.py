from typing import Optional, Literal, Annotated
from datetime import date, datetime
from pydantic import Field, AfterValidator

from src.api.auth.schemas import ProfileBase, PhoneStr, login_validation, birth_validator, EmailStr, NameStr


class FullProfileBase(ProfileBase):
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
    created_at: datetime


class UpdateProfileRequest(FullProfileBase):
    login: Optional[Annotated[str, AfterValidator(login_validation)]] = None
    email: Optional[EmailStr] = None
    first_name: Optional[NameStr] = None
    last_name: Optional[NameStr] = None
    gender: Optional[Literal["male", "female"]] = None
    birth: Optional[Annotated[date, AfterValidator(birth_validator)]] = None



