from fastapi import APIRouter, HTTPException
from fastapi.params import Depends

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import CurrentUser
from src.api.users.schemas import UpdateProfileRequest, ReadProfileResponse
from src.api.users.user_mapper import UserMapper
from src.datebase.dependencies import get_uow
from src.repositories.exceptions import RepositoryError
from src.datebase.dbmanager import DBManager
from src.services import UserService
from src.services.exceptions import UserNotFoundError, LoginAlreadyExistsError, EmailAlreadyExistsError, \
    FieldCannotBeChangedError


users_router = APIRouter(prefix="/profile")


@users_router.get("/me", response_model=ReadProfileResponse)
async def get_my_profile(
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = UserService(uow)

    try:
        auth_user = await service.get_user_profile_or_fail(user.id)

    except UserNotFoundError:
        raise HTTPException(401, "Invalid credentials")

    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")

    return UserMapper.to_response(auth_user)


@users_router.get("/{user_id}", response_model=ReadProfileResponse)
async def get_user_profile(user_id: int, uow: DBManager = Depends(get_uow)):
    service = UserService(uow)

    try:
        auth_user = await service.get_user_profile_or_fail(user_id)

    except UserNotFoundError:
        raise HTTPException(404, "Invalid credentials")

    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")

    return UserMapper.to_response(auth_user)


@users_router.patch("/me", response_model=ReadProfileResponse)
async def update_user_profile(
    data: UpdateProfileRequest,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = UserService(uow)

    try:
        async with uow:
            auth_user = await service.update_user_profile(user.id, data)

    except UserNotFoundError:
        raise HTTPException(404, "Invalid credentials")

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
        raise HTTPException(500, "An internal server error occurred.")

    return UserMapper.to_response(auth_user)
