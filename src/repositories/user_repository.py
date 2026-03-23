from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from src.api.auth.schemas import RegisterRequest
from src.models import AuthUser, UserProfile
from src.repositories.exceptions import handle_repository_errors


class UserRepository:

    def __init__(self, db: AsyncSession):
        self.db = db


    async def get_user_by_login(
        self,
        login: str,
        with_profile: bool = False
    ):
        auth_user_query = select(AuthUser).where(AuthUser.login == login)

        options = [selectinload(AuthUser.profile)] if with_profile else []
        auth_user_query = auth_user_query.options(*options)

        return await self.db.scalar(auth_user_query)


    @handle_repository_errors
    async def get_user_by_id(self, user_id: int, with_profile: bool = False):
        auth_user_query = select(AuthUser).where(AuthUser.user_id == user_id)

        options = [selectinload(AuthUser.profile)] if with_profile else []
        auth_user_query = auth_user_query.options(*options)

        return await self.db.scalar(auth_user_query)

    @handle_repository_errors
    async def exists_login(self, login: str):
        login_exists = await self.db.scalar(
            select(AuthUser.login)
            .where(AuthUser.login == login)
        )

        return bool(login_exists)

    @handle_repository_errors
    async def exists_email(self, email: str):
        email_exists = await self.db.scalar(
            select(AuthUser.email)
            .where(AuthUser.email == email)
        )

        return bool(email_exists)

    @handle_repository_errors
    async def add_auth_user(self, user: RegisterRequest):
        auth_user = AuthUser(
            login=user.login,
            email=user.email,
            password_hash=user.password,
            profile=UserProfile(
                first_name=user.first_name,
                last_name=user.last_name,
                gender=user.gender,
                birth=user.birth
            )
        )

        self.db.add(auth_user)

        return auth_user

    @handle_repository_errors
    async def update_auth_user_profile(
            self,
            user_id: int,
            auth_fields: dict,
            profile_fields: dict,
    ):
        if auth_fields:
            await self.db.execute(
                update(AuthUser)
                .where(AuthUser.user_id == user_id)
                .values(**auth_fields)
            )

        if profile_fields:
            await self.db.execute(
                update(UserProfile)
                .where(UserProfile.user_id == user_id)
                .values(**profile_fields)
            )

        auth_user = await self.db.scalar(
            select(AuthUser)
            .where(AuthUser.user_id == user_id)
            .options(selectinload(AuthUser.profile))
        )

        return auth_user

