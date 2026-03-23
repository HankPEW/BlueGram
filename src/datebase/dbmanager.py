from src.repositories import UserRepository, PostRepository, CommentRepository, AuthRepository


class DBManager:

    def __init__(self, session_factory):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.session = self.session_factory()

        self.users = UserRepository(self.session)
        self.auth = AuthRepository(self.session)
        self.posts = PostRepository(self.session)
        self.comments = CommentRepository(self.session)

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()

        await self.session.close()

    async def commit(self):
        if self.session:
            await self.session.commit()