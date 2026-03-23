from sqlalchemy.exc import IntegrityError

from src.api.users.schemas import UpdateProfileRequest
from src.datebase.dbmanager import DBManager
from src.services.constances import ALLOWED_FIELDS_IN_PROFILE, ALLOWED_FIELDS_IN_AUTH
from src.services.exceptions import UserNotFoundError, FieldCannotBeChangedError, LoginAlreadyExistsError, \
    EmailAlreadyExistsError


class UserService:

    def __init__(self, uow: DBManager):
        self.uow = uow

    async def get_user_profile_or_fail(self, user_id: int):
        auth_user = await self.uow.users.get_user_by_id(user_id, with_profile=True)

        if auth_user is None:
            raise UserNotFoundError()

        return auth_user

    async def update_user_profile(self, user_id: int, data: UpdateProfileRequest):
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
            user = await self.uow.users.update_auth_user_profile(
                user_id=user_id,
                auth_fields=auth_fields,
                profile_fields=profile_fields
            )
            if user is None:
                raise UserNotFoundError()

            await self.uow.commit()

            return user

        except IntegrityError as e:
            err = str(e.orig)
            if "uq_users_login" in err:
                raise LoginAlreadyExistsError()
            if "uq_users_email" in err:
                raise EmailAlreadyExistsError()
            raise
