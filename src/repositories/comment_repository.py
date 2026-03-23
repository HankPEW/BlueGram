from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.api.comments.schemas import UpdateCommentRequest, CreateCommentRequest
from src.models import PostComment, CommentLike
from src.repositories.exceptions import handle_repository_errors


class CommentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    @handle_repository_errors
    async def get_post_comments(self, post_id: int, limit: int, offset: int):
        comments = await self.db.scalars(
            select(PostComment)
            .options(selectinload(PostComment.user))
            .where(PostComment.post_id == post_id)
            .order_by(PostComment.likes_count)
            .limit(limit)
            .offset(offset)
        )

        return comments

    @handle_repository_errors
    async def get_comment(self, comment_id: int):
        comment = await self.db.scalar(
            select(PostComment)
            .options(selectinload(PostComment.user))
            .where(PostComment.comment_id == comment_id)
        )

        return comment

    @handle_repository_errors
    async def add_comment(self, data: CreateCommentRequest, post_id: int, user_id: int):
        new_comment = await self.db.execute(
            insert(PostComment)
            .values(
                user_id=user_id,
                post_id=post_id,
                comment_text=data.comment_text
            )
            .returning(PostComment)
        )

        new_comment = new_comment.scalar_one()

        return await self.get_comment(new_comment.comment_id)

    @handle_repository_errors
    async def update_comment(self, data: UpdateCommentRequest, comment_id: int, user_id: int):
        updated_comment_id = await self.db.execute(
            update(PostComment)
            .where(
                PostComment.comment_id == comment_id,
                PostComment.user_id == user_id
            )
            .values(comment_text=data.comment_text)
            .returning(PostComment.comment_id)
        )

        return updated_comment_id.scalar()

    @handle_repository_errors
    async def delete_comment(self, comment_id: int, user_id: int):
        comment_post_id = await self.db.execute(
            delete(PostComment)
            .where(
                PostComment.comment_id == comment_id,
                PostComment.user_id == user_id
            )
            .returning(PostComment.post_id)
        )

        return comment_post_id.scalar()

    @handle_repository_errors
    async def get_comment_like(self, user_id: int, comment_id: int):
        existing_like = await self.db.scalar(
            select(CommentLike)
            .where(
                CommentLike.comment_id == comment_id,
                CommentLike.user_id == user_id
            )
        )

        return existing_like

    @handle_repository_errors
    async def add_comment_like(self, comment_id: int, user_id: int):
        await self.db.execute(
            insert(CommentLike)
            .values(comment_id=comment_id, user_id=user_id)
            .on_conflict_do_nothing()
        )

    @handle_repository_errors
    async def increment_comment_likes_count(self, comment_id: int):
        await self.db.execute(
            update(PostComment)
            .where(PostComment.comment_id == comment_id)
            .values(likes_count=PostComment.likes_count + 1)
        )

    @handle_repository_errors
    async def delete_comment_like(self, existing_like: CommentLike):
        await self.db.delete(existing_like)

    @handle_repository_errors
    async def decrement_comment_likes_count(self, comment_id: int):
        await self.db.execute(
            update(PostComment)
            .where(PostComment.comment_id == comment_id)
            .values(likes_count=PostComment.likes_count - 1)
        )

    async def get_comment_likes(self, comment_id: int, limit: int, offset: int):
        comment_likes = await self.db.scalars(
            select(CommentLike)
            .where(CommentLike.comment_id == comment_id)
            .options(selectinload(CommentLike.user))
            .limit(limit)
            .offset(offset)
        )

        return comment_likes
