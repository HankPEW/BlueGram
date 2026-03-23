from fastapi import APIRouter, HTTPException, Response, Depends, Request

from src.api.auth.auth_user_mapper import AuthUserMapper
from src.api.auth.schemas import RegisterRequest, LoginRequest, ReadCurrentUser, TokenPair
from src.datebase.dependencies import get_uow

from src.repositories.exceptions import RepositoryError
from src.services.auth_service import AuthUserService, AuthServiceJWT, RefreshTokenExpiredError, \
    RefreshTokenNotFoundError
from src.services.exceptions import UserNotFoundError, LoginIsExistsError, EmailIsExistsError, \
    RegisterAuthUserError
from src.datebase.dbmanager import DBManager
from src.settings import settings


auth_router = APIRouter()


def _set_token_cookies(response: Response, access_token: str, refresh_token: str) -> None:
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
        uow: DBManager = Depends(get_uow)
):
    jwt_service = AuthServiceJWT(uow)
    try:
        access_token, refresh_token = await jwt_service.login(user.login, user.password)
    except UserNotFoundError:
        raise HTTPException(401, "Wrong login or password.")
    _set_token_cookies(response, access_token, refresh_token)

    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@auth_router.post("/register", status_code=201, response_model=ReadCurrentUser)
async def registration(
        user: RegisterRequest,
        uow: DBManager = Depends(get_uow)
):
    service = AuthUserService(uow)

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
        raise HTTPException(500, "An internal server error occurred.")

    return AuthUserMapper.to_response(
        "User has been registered.",
        auth_user
    )

@auth_router.post("/token/refresh",response_model=TokenPair, summary="Обновление access/refresh токенов")
async def refresh_tokens(
    request: Request, response: Response, uow: DBManager = Depends(get_uow)
):
    jwt_service = AuthServiceJWT(uow)
    try:
        refresh_token = request.cookies.get(settings.refresh_cookie_name)
        pair = await jwt_service.refresh(refresh_token)
    except RefreshTokenExpiredError:
        raise HTTPException(401, detail="Refresh token has expired.")
    except RefreshTokenNotFoundError:
        raise HTTPException(401, detail="Refresh token not found.")
    except UserNotFoundError:
        raise HTTPException(401, detail="User not found.")

    _set_token_cookies(response, pair.access_token, pair.refresh_token)

    return pair


@auth_router.post("/logout", summary="Logout")
async def logout(
        request: Request,
        response: Response,
        db: DBManager = Depends(get_uow)
):
    service = AuthServiceJWT(db)

    try:
        refresh_token = request.cookies.get(settings.refresh_cookie_name)

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