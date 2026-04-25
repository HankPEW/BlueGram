from src.database.db import async_session_maker
from src.database.dbmanager import DBManager

async def get_uow():
    """Возвращает Unit of Work для работы с репозиториями."""
    async with DBManager(async_session_maker) as uow:
        yield uow
