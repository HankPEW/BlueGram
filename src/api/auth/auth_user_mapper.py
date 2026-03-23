from typing import Union

from src.api.auth.schemas import ReadCurrentUser, CurrentUser
from src.models import AuthUser


class AuthUserMapper:

    @staticmethod
    def to_response(message: str, auth_user: Union[AuthUser, CurrentUser]) -> ReadCurrentUser:
        return ReadCurrentUser(
            message=message,
            id=auth_user.user_id if isinstance(auth_user, AuthUser) else auth_user.id,
            login=auth_user.login
        )
