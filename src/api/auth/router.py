from fastapi import APIRouter, Depends, HTTPException, Response,  Request

from src.api.auth.auth_user_mapper import AuthUserMapper
from src.api.auth.schemas import (
    LoginRequest,
    ReadCurrentUser,
    RegisterRequest,
    TokenPair
)
from src.repositories.exceptions import RepositoryError
from src.services.auth_service import (
    AuthUserService,
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError
)
from src.services.dependencies.auth_user import get_auth_user_service
from src.services.exceptions import (
    EmailIsExistsError,
    LoginIsExistsError,
    RegisterAuthUserError,
    UserNotFoundError

)
from src.settings import settings


auth_router = APIRouter(tags=["AuthUsers"])


def _set_token_cookies(
    response: Response,
    access_token: str,
    refresh_token: str
):
    """Устанавливает access и refresh токены в cookies ответа."""
    response.set_cookie(
        key=settings.access_cookie_name,
        value=access_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=settings.access_token_expires_minutes * 60,
        domain=settings.session_cookie_domain,
        path="/",
    )
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.session_cookie_secure,
        samesite="lax",
        max_age=settings.refresh_token_expires_minutes * 60,
        domain=settings.session_cookie_domain,
        path="/",
    )


@auth_router.post("/login")
async def login(
    user: LoginRequest,
    response: Response,
    service: AuthUserService = Depends(get_auth_user_service)
) -> TokenPair:
    """Аутентифицирует пользователя и возвращает пару JWT токенов."""
    try:
        access_token, refresh_token = await service.login(
            user.login,
            user.password
        )
    except UserNotFoundError:
        raise HTTPException(401, "Wrong login or password.")

    _set_token_cookies(response, access_token, refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_router.post(
    "/register",
    status_code=201,
    response_model=ReadCurrentUser
)
async def registration(
    user: RegisterRequest,
    service: AuthUserService = Depends(get_auth_user_service)
) -> ReadCurrentUser:
    """Регистрирует нового пользователя и возвращает его данные."""
    try:
        auth_user = await service.user_registration(user)
    except LoginIsExistsError:
        raise HTTPException(
            409,
            "The login you wrote has already been registered."
        )
    except EmailIsExistsError:
        raise HTTPException(
            409,
            "The email you wrote has already been registered."
        )
    except RegisterAuthUserError:
        raise HTTPException(
            409,
            "User with these credentials already exists."
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return AuthUserMapper.to_response(
        "User has been registered.",
        auth_user
    )


@auth_router.post(
    "/token/refresh",
    response_model=TokenPair,
    summary="Обновление access/refresh токенов"
)
async def refresh_tokens(
    request: Request,
    response: Response,
    service: AuthUserService = Depends(get_auth_user_service)
) -> TokenPair:
    """Обновляет access и refresh токены по refresh токену."""
    try:
        refresh_token = request.cookies.get(
            settings.refresh_cookie_name
        )
        pair = await service.refresh(refresh_token)
    except RefreshTokenExpiredError:
        raise HTTPException(401, detail="Refresh token has expired.")
    except RefreshTokenNotFoundError:
        raise HTTPException(401, detail="Refresh token not found.")
    except UserNotFoundError:
        raise HTTPException(401, detail="User not found.")

    _set_token_cookies(
        response,
        pair.access_token,
        pair.refresh_token
    )

    return pair


@auth_router.post("/logout", summary="Logout")
async def logout(
    request: Request,
    response: Response,
    service: AuthUserService = Depends(get_auth_user_service)
):
    """Выход пользователя с удалением refresh токена и cookies."""
    try:
        refresh_token = request.cookies.get(
            settings.refresh_cookie_name
        )

        if not refresh_token:
            raise HTTPException(401, "Refresh token missing")

        await service.logout(refresh_token)

    except RefreshTokenNotFoundError:
        raise HTTPException(
            401,
            "Refresh token not found or already revoked"
        )

    response.delete_cookie(settings.access_cookie_name)
    response.delete_cookie(settings.refresh_cookie_name)

    return {"detail": "User has logged out"}
