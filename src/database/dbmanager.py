from src.repositories import (
    AuthRepository,
    CommentRepository,
    PostRepository,
    UserRepository
)


class DBManager:
    """Контекстный менеджер для управления сессией базы данных."""

    def __init__(self, session_factory):
        """Инициализирует DBManager с фабрикой сессий."""
        self.session_factory = session_factory

    async def __aenter__(self):
        """Создаёт сессию и инициализирует репозитории."""
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.auth = AuthRepository(self.session)
        self.posts = PostRepository(self.session)
        self.comments = CommentRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрывает сессию и откатывает транзакцию при ошибке."""
        if exc_type:
            await self.session.rollback()

        await self.session.close()

    async def commit(self):
        """Коммит изменения в базе данных."""
        if self.session:
            await self.session.commit()
