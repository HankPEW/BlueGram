from fastapi import Depends

from src.database.dbmanager import DBManager
from src.database.dependencies import get_uow
from src.services import PostService


def get_post_service(
    uow: DBManager = Depends(get_uow)
) -> PostService:
    return PostService(uow)
