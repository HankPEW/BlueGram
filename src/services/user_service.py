from sqlalchemy.exc import IntegrityError

from src.api.users.schemas import UpdateProfileRequest, ReadProfileResponse
from src.api.users.user_mapper import UserMapper
from src.database.dbmanager import DBManager
from src.services.constances import (
    ALLOWED_FIELDS_IN_AUTH,
    ALLOWED_FIELDS_IN_PROFILE
)
from src.services.exceptions import (
    EmailAlreadyExistsError,
    FieldCannotBeChangedError,
    LoginAlreadyExistsError,
    UserNotFoundError
)


class UserService:
    """Сервис для работы с пользователями."""

    def __init__(self, uow: DBManager):
        """Инициализация сервиса."""
        self.uow = uow

    async def get_user_profile_or_fail(
        self,
        user_id: int
    ) -> ReadProfileResponse:
        """Возвращает профиль пользователя или вызывает ошибку."""
        auth_user = await self.uow.users.get_user_by_id(user_id, with_profile=True)

        if auth_user is None:
            raise UserNotFoundError()

        return UserMapper.to_response(auth_user)

    async def update_user_profile(
        self,
        user_id: int,
        data: UpdateProfileRequest
    ) -> ReadProfileResponse:
        """Обновляет профиль пользователя."""
        update_data = data.model_dump(exclude_unset=True)

        if not update_data:
            raise FieldCannotBeChangedError()

        auth_fields = {}
        profile_fields = {}

        for field, value in update_data.items():
            if field in ALLOWED_FIELDS_IN_PROFILE:
                profile_fields[field] = value
            elif field in ALLOWED_FIELDS_IN_AUTH:
                auth_fields[field] = value
            else:
                raise FieldCannotBeChangedError()

        try:
            auth_user = await self.uow.users.update_auth_user_profile(
                user_id=user_id,
                auth_fields=auth_fields,
                profile_fields=profile_fields
            )
            if auth_user is None:
                raise UserNotFoundError()

            await self.uow.commit()

            return UserMapper.to_response(auth_user)

        except IntegrityError as e:
            err = str(e.orig)
            if "uq_users_login" in err:
                raise LoginAlreadyExistsError()
            if "uq_users_email" in err:
                raise EmailAlreadyExistsError()
            raise
