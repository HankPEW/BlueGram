import string
from typing import Annotated, Literal

from pydantic import BaseModel, AfterValidator, EmailStr, Field, model_validator
from datetime import date, datetime

from pydantic_core import PydanticCustomError


ALLOWED_CHARS = string.ascii_letters + string.digits


LoginStr = Annotated[
    str,
    Field(
        min_length=7,
        max_length=20,
        pattern=r"^(?=.*[A-Za-z])[{ALLOWED_CHARS}]+$"
    )
]


PasswordStr = Annotated[
    str,
    Field(
        min_length=7,
        max_length=20,
        pattern=(
            r"^(?=.*[A-Za-z])(?=.*[0-9])(?=.*[{string.punctuation}])"
            f"[{ALLOWED_CHARS + string.punctuation}]+$"
        )
    )
]


PhoneStr = Annotated[
    str,
    Field(min_length=10, max_length=15, pattern=r"^\+?\d+$")
]


NameStr = Annotated[
    str,
    Field(min_length=1, max_length=20, pattern=r"^[^\W\d_]+$")
]


def login_validation(login: str) -> str:
    contains_allowed_chars = all(x in ALLOWED_CHARS for x in login)
    contains_letter = any(x in string.ascii_letters for x in login)

    if not contains_allowed_chars:
        raise PydanticCustomError(
            "InvalidUserFormat",
            "The login may contain only latin letters and digits."
        )

    if not contains_letter:
        raise PydanticCustomError(
            "InvalidLoginFormat",
            "The login must contain at least one latin letter."
        )

    if not 6 < len(login) < 21:
        raise PydanticCustomError(
            "InvalidLoginLength",
            "The login must contain more than 6 and less than 20 symbols."
        )

    return login


def password_validation(password: str) -> str:
    contains_allowed_chars = all(
        x in ALLOWED_CHARS + string.punctuation
        for x in password
    )
    contains_letter = any(x in string.ascii_letters for x in password)
    contains_special_symbol = any(x in string.punctuation for x in password)
    contains_digit = any(x in string.digits for x in password)

    if not contains_allowed_chars:
        raise PydanticCustomError(
            "InvalidPasswordFormat",
            (
                "The password may contain only latin letters, "
            "digits and special symbols."
            )
        )

    if not contains_letter:
        raise PydanticCustomError(
            "InvalidPasswordFormat",
            "The password must contain at least one latin letter."
        )

    if not contains_digit:
        raise PydanticCustomError(
            "InvalidPasswordFormat",
            "The password must contain at least one digit."
        )

    if not contains_special_symbol:
        raise PydanticCustomError(
            "InvalidPasswordFormat",
            "The password must contain at least one special symbol."
        )

    if not 6 < len(password) < 21:
        raise PydanticCustomError(
            "InvalidPasswordLength",
            "The password must contain more than 6 and less than 20 symbols."
        )

    return password


def birth_validator(birth: date) -> date:
    if birth < date(1900, 1, 1):
        raise PydanticCustomError(
            "InvalidDatePastValue",
            "Your date of birth must be after January 1, 1900. "
        )

    if birth > date.today():
        raise PydanticCustomError(
            "InvalidDateFutureValue",
            "Your date of birth must be today or early."
        )

    return birth


class ProfileBase(BaseModel):
    login: Annotated[str, AfterValidator(login_validation)]
    email: EmailStr
    first_name: NameStr
    last_name: NameStr
    gender: Literal["male", "female"]
    birth: Annotated[date, AfterValidator(birth_validator)]

class RegisterRequest(ProfileBase):
    password: Annotated[str, AfterValidator(password_validation)]
    repeated_password: str
    created_at: datetime

    @model_validator(mode="after")
    def password_match_validation(self):
        if not self.password == self.repeated_password:
            raise PydanticCustomError(
                "InvalidPasswordMatchValidation",
                "Your repeated password must match your password."
            )
        return self


class LoginRequest(BaseModel):
    login: str = Field(min_length=7, max_length=20)
    password: str = Field(min_length=7, max_length=20)


class CurrentUser(BaseModel):
    id: int
    login: str


class ReadCurrentUser(CurrentUser):
    message: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str

class RefreshRequest(BaseModel):
    refresh_token: str