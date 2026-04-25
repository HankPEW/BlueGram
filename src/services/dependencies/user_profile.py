from fastapi.params import Depends

from src.database.dbmanager import DBManager
from src.database.dependencies import get_uow
from src.services import UserService


def get_user_profile_service(
    uow: DBManager = Depends(get_uow)
) -> UserService:
    return UserService(uow)
