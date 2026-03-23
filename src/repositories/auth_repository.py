from datetime import datetime
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from src.models import RefreshToken


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_refresh_token(self, user_id: int, token_hash: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at
        )

        self.session.add(token)
        await self.session.flush()

        return token

    async def get_refresh_token(self, token_hash: str) -> Optional[RefreshToken]:
        return await self.session.scalar(
            select(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
        )

    async def delete_refresh_token(self, token_obj: RefreshToken) -> None:
        await self.session.delete(token_obj)

    async def revoke_token(self, user_id: int) -> None:
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(revoked=True)
        )
        await self.session.execute(stmt)