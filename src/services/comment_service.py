from typing import List

from sqlalchemy.exc import IntegrityError

from src.api.comments.comment_like_mapper import CommentLikeMapper
from src.api.comments.comment_mapper import CommentMapper
from src.api.comments.schemas import (
    CreateCommentRequest,
    ReadCommentResponse,
    UpdateCommentRequest, CommentLikeResponse
)
from src.database.dbmanager import DBManager
from src.services.exceptions import (
    AddPostCommentError,
    DeletePostCommentError,
    ReadPostCommentError,
    ReadPostError,
    ToggleCommentLikeError,
    UpdatePostCommentError
)


class PostCommentService:
    """Сервис для работы с комментариями к постам."""

    def __init__(self, uow: DBManager):
        """Инициализация сервиса."""
        self.uow = uow

    async def read_post_comments(
        self,
        post_id: int,
        limit: int,
        offset: int
    ) -> List[ReadCommentResponse]:
        """Возвращает список комментариев поста."""
        post = await self.uow.posts.get_post(post_id)

        if post is None:
            raise ReadPostError()

        post_comments = await self.uow.comments.get_post_comments(
            post_id,
            limit,
            offset
        )

        return [
            CommentMapper.to_response(comment)
            for comment in post_comments
        ]

    async def read_comment(
        self,
        comment_id: int
    ) -> ReadCommentResponse:
        """Возвращает один комментарий по ID."""
        post_comment = await self.uow.comments.get_comment(comment_id)

        if post_comment is None:
            raise ReadPostCommentError()

        return CommentMapper.to_response(post_comment)

    async def create_comment(
        self,
        data: CreateCommentRequest,
        post_id: int,
        user_id: int
    ) -> ReadCommentResponse:
        """Создаёт новый комментарий."""
        post = await self.uow.posts.get_post(post_id)

        if post is None:
            raise ReadPostError()

        try:
            new_comment = await self.uow.comments.add_comment(
                data,
                post_id,
                user_id
            )

            if new_comment is None:
                raise AddPostCommentError()

            await self.uow.posts.increment_comment_count(
                new_comment.post_id
            )
            await self.uow.commit()

            return CommentMapper.to_response(new_comment)

        except IntegrityError:
            raise AddPostCommentError()

    async def update_comment(
        self,
        data: UpdateCommentRequest,
        user_id: int,
        comment_id: int
    ) -> ReadCommentResponse:
        try:
            updated_comment_id = await self.uow.comments.update_comment(
                data,
                comment_id,
                user_id
            )

            if updated_comment_id is None:
                raise UpdatePostCommentError()

            await self.uow.commit()

            updated_comment = await self.uow.comments.get_comment(
                updated_comment_id
            )

            return CommentMapper.to_response(updated_comment)

        except IntegrityError:
            raise UpdatePostCommentError()

    async def delete_comment(
        self,
        comment_id: int,
        user_id: int
    ):
        """Удаляет комментарий."""
        try:
            deleted_comment_post_id = (
                await self.uow.comments.delete_comment(
                    comment_id,
                    user_id
                )
            )

            if deleted_comment_post_id is None:
                raise DeletePostCommentError()

            await self.uow.posts.decrement_comment_count(
                deleted_comment_post_id
            )
            await self.uow.commit()

        except IntegrityError:
            raise DeletePostCommentError()

    async def toggle_comment_like(
        self,
        comment_id: int,
        user_id: int
    ) -> ReadCommentResponse:
        """Переключает лайк комментария."""
        post_comment = await self.uow.comments.get_comment(comment_id)

        if post_comment is None:
            raise ReadPostCommentError()

        existing_like = await self.uow.comments.get_comment_like(
            user_id,
            comment_id
        )
        try:
            if existing_like:
                await self.uow.comments.delete_comment_like(
                    existing_like
                )
                await self.uow.comments.decrement_comment_likes_count(
                    comment_id
                )

            else:
                await self.uow.comments.add_comment_like(
                    comment_id,
                    user_id
                )
                await self.uow.comments.increment_comment_likes_count(
                    comment_id
                )

            await self.uow.commit()

        except IntegrityError:
            raise ToggleCommentLikeError()

        post_comment = await self.uow.comments.get_comment(comment_id)

        return CommentMapper.to_response(post_comment)

    async def get_comment_likes(
        self,
        comment_id: int,
        limit: int,
        offset: int
    ) -> List[CommentLikeResponse]:
        """Возвращает список лайков комментария."""
        comment = await self.uow.comments.get_comment(comment_id)

        if comment is None:
            raise ReadPostCommentError()

        likes = await self.uow.comments.get_comment_likes(
            comment_id,
            limit,
            offset
        )

        return CommentLikeMapper.list_to_response(likes)
