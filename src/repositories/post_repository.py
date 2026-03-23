from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, update, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import selectinload

from src.api.posts.schemas import UpdatePostRequest, CreatePostRequest
from src.models import Post, PostLike
from src.repositories.exceptions import handle_repository_errors


class PostRepository:

    def __init__(self, db: AsyncSession):
        self.db = db

    @handle_repository_errors
    async def get_all_posts(self, limit: int, offset: int):
        posts = await self.db.scalars(
            select(Post)
            .options(selectinload(Post.user))
            .order_by(desc(Post.created_at))
            .limit(limit)
            .offset(offset)
        )

        return posts

    @handle_repository_errors
    async def get_post(self, post_id: int):
        post = await self.db.scalar(
            select(Post)
            .where(Post.post_id == post_id)
            .options(selectinload(Post.user))
        )

        return post

    @handle_repository_errors
    async def add_post(self, data: CreatePostRequest, user_id: int):
        post_id = await self.db.execute(
            insert(Post)
            .values(user_id=user_id, title=data.title, body=data.body)
            .returning(Post.post_id)
        )
        post_id = post_id.scalar_one_or_none()

        return post_id

    @handle_repository_errors
    async def update_post(self, post_id: int, user_id: int, data: UpdatePostRequest):
        data = data.model_dump(exclude_unset=True)

        updated_post_id = await self.db.execute(
            update(Post)
            .where(
                Post.post_id == post_id,
                Post.user_id == user_id
            )
            .values(**data)
            .returning(Post.post_id)
        )

        return updated_post_id.scalar_one_or_none()

    @handle_repository_errors
    async def delete_post(self, post_id: int, user_id: int):
        post = await self.db.execute(
            delete(Post)
            .where(Post.post_id == post_id, Post.user_id == user_id)
            .returning(Post.post_id)
        )

        return post.scalar()

    @handle_repository_errors
    async def increment_post_likes_count(self, post_id: int):
        await self.db.execute(
            update(Post)
            .where(Post.post_id == post_id)
            .values(likes_count=Post.likes_count + 1)
        )

    @handle_repository_errors
    async def decrement_post_likes_count(self, post_id: int):
        await self.db.execute(
            update(Post)
            .where(Post.post_id == post_id)
            .values(likes_count=Post.likes_count - 1)
        )

    @handle_repository_errors
    async def increment_comment_count(self, post_id: int):
        await self.db.execute(
            update(Post)
            .where(Post.post_id == post_id)
            .values(comments_count=Post.comments_count + 1)
        )

    @handle_repository_errors
    async def decrement_comment_count(self, post_id: int):
        await self.db.execute(
            update(Post)
            .where(Post.post_id == post_id)
            .values(comments_count=Post.comments_count - 1)
        )

    @handle_repository_errors
    async def get_post_like(self, post_id: int, user_id: int):
        existing_like = await self.db.scalar(
            select(PostLike)
            .where(
                PostLike.post_id == post_id,
                PostLike.user_id == user_id
            )
        )

        return existing_like

    @handle_repository_errors
    async def get_post_likes(self, post_id: int, limit: int, offset: int):
        post_likes = await self.db.scalars(
            select(PostLike)
            .where(PostLike.post_id == post_id)
            .options(selectinload(PostLike.user))
            .limit(limit)
            .offset(offset)
        )

        return post_likes

    @handle_repository_errors
    async def add_post_like(self, post_id: int, user_id: int):
        post_like = await self.db.execute(
            insert(PostLike)
            .values(post_id=post_id, user_id=user_id)
            .on_conflict_do_nothing()
            .returning(PostLike)
        )

        return post_like.scalar_one()

    @handle_repository_errors
    async def delete_post_like(self, existing_like: PostLike):
        await self.db.delete(existing_like)

