from fastapi import APIRouter, Depends, HTTPException

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import CurrentUser
from src.api.users.schemas import ReadProfileResponse, UpdateProfileRequest
from src.repositories.exceptions import RepositoryError
from src.services import UserService
from src.services.dependencies.user_profile import get_user_profile_service
from src.services.exceptions import (
    EmailAlreadyExistsError,
    FieldCannotBeChangedError,
    LoginAlreadyExistsError,
    UserNotFoundError,
)


users_router = APIRouter(prefix="/profile", tags=["Profiles"])


@users_router.get("/me", response_model=ReadProfileResponse)
async def get_my_profile(
    user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_profile_service)
) -> ReadProfileResponse:
    """Возвращает профиль текущего пользователя."""
    try:
        auth_user = await service.get_user_profile_or_fail(user.id)
    except UserNotFoundError:
        raise HTTPException(
            401,
            "Invalid credentials"
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return auth_user


@users_router.get(
    "/{user_id}",
    response_model=ReadProfileResponse
)
async def get_user_profile(
    user_id: int,
    service: UserService = Depends(get_user_profile_service)
) -> ReadProfileResponse:
    """Возвращает профиль пользователя по его ID."""
    try:
        auth_user = await service.get_user_profile_or_fail(user_id)
    except UserNotFoundError:
        raise HTTPException(
            404,
            "Invalid credentials"
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return auth_user


@users_router.patch(
    "/me",
    response_model=ReadProfileResponse
)
async def update_user_profile(
    data: UpdateProfileRequest,
    user: CurrentUser = Depends(get_current_user),
    service: UserService = Depends(get_user_profile_service)
) -> ReadProfileResponse:
    """Обновляет профиль текущего пользователя."""
    try:
        auth_user = await service.update_user_profile(user.id, data)
    except UserNotFoundError:
        raise HTTPException(
            404,
            "Invalid credentials"
        )
    except LoginAlreadyExistsError:
        raise HTTPException(
            409,
            "The login you wrote has already been registered."
        )
    except EmailAlreadyExistsError:
        raise HTTPException(
            409,
            "The email you wrote has already been registered."
        )
    except FieldCannotBeChangedError:
        raise HTTPException(
        403,
        "Field can not be updated."
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return auth_user
