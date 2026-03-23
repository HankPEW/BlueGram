from src.datebase.db import AsyncSessionLocal
from src.datebase.dbmanager import DBManager


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def get_uow():
    async with DBManager(AsyncSessionLocal) as uow:
        yield uow