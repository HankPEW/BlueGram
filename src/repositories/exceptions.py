from sqlalchemy.exc import SQLAlchemyError


class RepositoryError(Exception):
    pass


def handle_repository_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)

        except SQLAlchemyError as e:
            raise RepositoryError(f"Repository error in {func.__name__}") from e

    return wrapper