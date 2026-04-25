from fastapi import Depends

from src.database.dbmanager import DBManager
from src.database.dependencies import get_uow
from src.services import PostCommentService


def get_comment_service(
    uow: DBManager = Depends(get_uow)
) -> PostCommentService:
    return PostCommentService(uow)
