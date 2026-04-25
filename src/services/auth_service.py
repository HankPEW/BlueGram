from datetime import datetime, timedelta, timezone

from passlib.hash import argon2

from src.api.auth.schemas import RegisterRequest, TokenPair
from src.api.auth.tokens import tokens
from src.database.dbmanager import DBManager
from src.models import AuthUser, RefreshToken
from src.services.exceptions import (
    AddAuthUserError,
    EmailIsExistsError,
    LoginIsExistsError,
    RefreshTokenExpiredError,
    RefreshTokenNotFoundError,
    RegisterAuthUserError,
    UserNotFoundError,
    WrongPasswordError,
)
from src.settings import settings


class Security:
    """Класс для работы с безопасностью паролей."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Хешируем пароль через Argon2."""
        return argon2.hash(password)

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Проверяем пароль."""
        return argon2.verify(password, hashed)


class AuthUserService:
    """Сервис для работы с авторизацией."""

    def __init__(self, uow: DBManager):
        """Инициализация сервиса."""
        self.uow = uow

    async def login(
        self,
        login: str,
        password: str
    ) -> tuple[str, str]:
        """Выполняет вход и возвращает пару токенов."""
        user = await self._get_user_or_raise(login, password)
        pair = await self._issue_tokens(user.user_id, user.login)
        return pair.access_token, pair.refresh_token

    async def _get_login_or_not(self, login: str):
        """Проверяет уникальность логина."""
        login_exists = await self.uow.users.exists_login(login)

        if login_exists:
            raise LoginIsExistsError()

    async def _get_email_or_not(self, email: str):
        """Проверяет уникальность email."""
        email_exists = await self.uow.users.exists_email(email)

        if email_exists:
            raise EmailIsExistsError()

    async def user_registration(
        self,
        user: RegisterRequest
    ) -> AuthUser:
        """Регистрирует нового пользователя."""
        await self._get_login_or_not(user.login)
        await self._get_email_or_not(user.email)

        user.password = Security.hash_password(user.password)

        try:
            async with self.uow as uow:
                auth_user = await uow.users.add_auth_user(user)
                await uow.commit()
        except AddAuthUserError:
            raise RegisterAuthUserError()

        return auth_user

    async def refresh(self, raw_refresh_token: str) -> TokenPair:
        """Обновляет access и refresh токены."""
        async with self.uow:
            stored = await self._get_valid_refresh(raw_refresh_token)
            user = await self._get_user_for_token(stored.user_id)
            await self.uow.auth.delete_refresh_token(stored)
            pair = await self._issue_tokens(user.user_id, user.login)
            return pair

    async def _get_valid_refresh(self, raw_refresh_token: str) -> RefreshToken:
        """Проверяет валидность refresh токена."""
        token_hash = tokens.hash_session_token(raw_refresh_token)
        stored = await self.uow.auth.get_refresh_token(token_hash)

        if not stored or stored.revoked:
            raise RefreshTokenNotFoundError

        now = datetime.now(timezone.utc)

        if stored.expires_at <= now:
            await self.uow.auth.delete_refresh_token(stored)
            raise RefreshTokenExpiredError

        return stored

    async def _get_user_for_token(self, user_id: int) -> AuthUser:
        """Возвращает пользователя по ID из токена."""
        user = await self.uow.users.get_user_by_id(user_id)

        if not user:
            raise UserNotFoundError

        return user

    async def _get_user_or_raise(
        self,
        login: str,
        password: str
    ) -> AuthUser:
        """Проверяет пользователя и пароль."""
        auth_user = await self.uow.users.get_user_by_login(login)

        if auth_user is None:
            raise UserNotFoundError()

        password_verified = Security.verify_password(
            password,
            auth_user.password_hash
        )

        if not password_verified:
            raise WrongPasswordError()

        return auth_user

    @staticmethod
    def _refresh_expiry() -> datetime:
        """Возвращает время истечения refresh токена."""
        return datetime.now(timezone.utc) + timedelta(
            minutes=settings.refresh_token_expires_minutes
        )

    async def _issue_tokens(
        self,
        user_id: int,
        login: str
    ) -> TokenPair:
        """Создаёт и сохраняет пару токенов."""
        access_token = tokens.create_access_token(user_id, login)
        refresh_token = tokens.create_refresh_token()
        refresh_hash = tokens.hash_session_token(refresh_token)
        expires_at = self._refresh_expiry()

        await self.uow.auth.create_refresh_token(
            user_id=user_id,
            token_hash=refresh_hash,
            expires_at=expires_at
        )
        await self.uow.session.commit()

        return TokenPair(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def logout(self, refresh_token: str):
        """Отзывает refresh токен пользователя."""
        token_hash = tokens.hash_session_token(refresh_token)

        token_obj = await self.uow.auth.get_refresh_token(token_hash)

        if not token_obj or token_obj.revoked:
            raise RefreshTokenNotFoundError

        token_obj.revoked = True
        await self.uow.commit()
