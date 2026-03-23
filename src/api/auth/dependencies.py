import jwt
from fastapi import Request, HTTPException, Depends

from src.api.auth.schemas import CurrentUser
from src.datebase.dependencies import get_uow
from src.datebase.dbmanager import DBManager
from src.settings import settings


async def get_current_user(
    request: Request,
    uow: DBManager = Depends(get_uow)
) -> CurrentUser:
    token = _extract_access_token(request)

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            401,
            "Access token expired"
        )

    except jwt.InvalidTokenError:
        raise HTTPException(
            401,
            "Invalid access token"
        )

    user_id = int(payload["sub"])

    auth_user = await uow.users.get_user_by_id(user_id)

    if not auth_user:
        raise HTTPException(
            401,
            "User not found"
        )

    return CurrentUser(
        id=auth_user.user_id,
        login=auth_user.login
    )


def _extract_access_token(request: Request) -> str:
    cookie_token = request.cookies.get("access_token")

    if cookie_token:
        return cookie_token

    raise HTTPException(
        401,
        "Missing access token"
    )
