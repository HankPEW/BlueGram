from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import RefreshToken


class AuthRepository:
    """Репозиторий для работы с токенами аутентификации."""

    def __init__(self, session: AsyncSession):
        """Инициализация репозитория с сессией базы данных."""
        self.session = session

    async def create_refresh_token(
        self,
        user_id: int,
        token_hash: str,
        expires_at: datetime
    ) -> RefreshToken:
        """Создаёт и сохраняет refresh-токен пользователя."""
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.session.add(token)
        await self.session.flush()

        return token

    async def get_refresh_token(
        self,
        token_hash: str
    ) -> Optional[RefreshToken]:
        """Возвращает refresh-токен по его хэшу."""
        return await self.session.scalar(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )

    async def delete_refresh_token(
        self,
        token_obj: RefreshToken
    ):
        """Удаляет refresh-токен из базы данных."""
        await self.session.delete(token_obj)

    async def revoke_token(
        self,
        user_id: int
    ):
        """Отзывает все refresh-токены пользователя."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)
