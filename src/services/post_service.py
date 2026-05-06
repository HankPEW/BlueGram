from typing import List

from sqlalchemy.exc import IntegrityError

from src.api.posts.post_likes_mapper import PostLikeMapper
from src.api.posts.post_mapper import PostMapper
from src.api.posts.schemas import CreatePostRequest, UpdatePostRequest, ReadPostResponse, PostLikeResponse
from src.database.dbmanager import DBManager
from src.services.exceptions import (
    AddPostError,
    DeletePostError,
    ReadPostError,
    TogglePostLikeError,
    UpdatePostError,
)


class PostService:
    """Сервис для работы с постами."""

    def __init__(self, uow: DBManager):
        """Инициализация сервиса."""
        self.uow = uow

    async def read_all_posts(
        self,
        limit: int,
        offset: int
    ) -> List[ReadPostResponse]:
        """Возвращает список постов."""
        posts = await self.uow.posts.get_all_posts(limit, offset)

        if posts is None:
            raise ReadPostError()

        return [PostMapper.to_response(post) for post in posts]

    async def read_post(self, post_id: int) -> ReadPostResponse:
        """Возвращает пост по ID."""
        post = await self.uow.posts.get_post(post_id)

        if post is None:
            raise ReadPostError()

        return PostMapper.to_response(post)

    async def create_post(
        self,
        data: CreatePostRequest,
        user_id: int
    ) -> ReadPostResponse:
        """Создаёт новый пост."""
        try:
            post_id = await self.uow.posts.add_post(data, user_id)

            if post_id is None:
                raise AddPostError()

            await self.uow.commit()

            post = await self.uow.posts.get_post(post_id)
            return PostMapper.to_response(post)

        except IntegrityError:
            raise AddPostError()

    async def update_post(
        self,
        data: UpdatePostRequest,
        post_id: int,
        user_id: int
    ) -> ReadPostResponse:
        """Обновляет пост."""
        try:
            updated_post_id = await self.uow.posts.update_post(
                post_id,
                user_id,
                data
            )

            if updated_post_id is None:
                raise UpdatePostError()

            await self.uow.commit()

            updated_post = await self.uow.posts.get_post(
                updated_post_id
            )

            return PostMapper.to_response(updated_post)

        except IntegrityError:
            raise UpdatePostError()

    async def delete_post(
        self,
        post_id: int,
        user_id: int
    ):
        """Удаляет пост."""
        try:
            deleted_post_id = await self.uow.posts.delete_post(
                post_id,
                user_id
            )

            if deleted_post_id is None:
                raise DeletePostError()

            await self.uow.commit()

        except IntegrityError:
            raise DeletePostError()

    async def toggle_post_like(
        self,
        post_id: int,
        user_id: int
    ) -> ReadPostResponse:
        """Переключает лайк поста."""
        post = await self.uow.posts.get_post(post_id)

        if post is None:
            raise ReadPostError()

        existing_like = await self.uow.posts.get_post_like(
            post_id,
            user_id
        )

        try:
            if existing_like:
                await self.uow.posts.delete_post_like(
                    existing_like
                )
                await self.uow.posts.decrement_post_likes_count(
                    post_id
                )
            else:
                await self.uow.posts.add_post_like(
                    post_id,
                    user_id
                )
                await self.uow.posts.increment_post_likes_count(
                    post_id
                )

            await self.uow.commit()

        except IntegrityError:
            raise TogglePostLikeError()

        post = await self.uow.posts.get_post(post_id)
        return PostMapper.to_response(post)

    async def get_post_likes(
        self,
        post_id: int,
        limit: int,
        offset: int
    ) -> List[PostLikeResponse]:
        """Возвращает список лайков поста."""
        post = await self.uow.posts.get_post(post_id)

        if post is None:
            raise ReadPostError()

        post_likes = await self.uow.posts.get_post_likes(
            post_id,
            limit,
            offset
        )

        return PostLikeMapper.list_to_response(post_likes)
