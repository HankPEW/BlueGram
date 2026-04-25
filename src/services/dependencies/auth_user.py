from fastapi import Depends

from src.database.dbmanager import DBManager
from src.database.dependencies import get_uow
from src.services import AuthUserService


def get_auth_user_service(
    uow: DBManager = Depends(get_uow)
) -> AuthUserService:
    return AuthUserService(uow)
