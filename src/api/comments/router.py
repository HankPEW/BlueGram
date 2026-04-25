from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import CurrentUser
from src.api.comments.schemas import (
    CommentLikeResponse,
    CreateCommentRequest,
    ReadCommentResponse,
    UpdateCommentRequest
)
from src.repositories.exceptions import RepositoryError
from src.services import PostCommentService
from src.services.dependencies.comment import get_comment_service
from src.services.exceptions import (
    AddPostCommentError,
    DeletePostCommentError,
    ReadPostCommentError,
    ToggleCommentLikeError,
    UpdatePostCommentError, ReadPostError
)


comments_router = APIRouter(tags=["Comments"])


@comments_router.get(
    "/{post_id}/comments",
    response_model=List[ReadCommentResponse]
)
async def read_comments(
    post_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: PostCommentService = Depends(get_comment_service)
) -> List[ReadCommentResponse]:
    """Получает список комментариев поста с пагинацией."""
    try:
        return await service.read_post_comments(
            post_id,
            limit,
            offset
        )
    except ReadPostError:
        raise HTTPException(404, "Post not found.")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.get(
    "/comments/{comment_id}",
    response_model=ReadCommentResponse
)
async def read_comment(
    comment_id: int,
    service: PostCommentService = Depends(get_comment_service)
) -> ReadCommentResponse:
    """Получает один комментарий по его ID."""
    try:
        return await service.read_comment(comment_id)
    except ReadPostCommentError:
        raise HTTPException(404, "Comment not found.")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.post(
    "/comments",
    response_model=ReadCommentResponse
)
async def create_comment(
    post_id: int,
    data: CreateCommentRequest,
    user: CurrentUser = Depends(get_current_user),
    service: PostCommentService = Depends(get_comment_service)
) -> ReadCommentResponse:
    """Создает новый комментарий к посту."""
    try:
        return await service.create_comment(
            data,
            post_id,
            user.id
        )
    except AddPostCommentError:
        raise HTTPException(
            400,
            "Comment cannot be created."
        )
    except ReadPostCommentError:
        raise HTTPException(
            404,
            "Comments not found."
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.patch(
    "/comments/{comment_id}",
    response_model=ReadCommentResponse
)
async def update_comment(
    comment_id: int,
    data: UpdateCommentRequest,
    user: CurrentUser = Depends(get_current_user),
    service: PostCommentService = Depends(get_comment_service)
) -> ReadCommentResponse:
    """Обновляет комментарий пользователя."""
    try:
        return await service.update_comment(
            data,
            user.id,
            comment_id
        )
    except UpdatePostCommentError:
        raise HTTPException(
            400,
            "Comment cannot be updated."
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.delete(
    "/comments/{comment_id}",
    status_code=204
)
async def delete_comment(
    comment_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: PostCommentService = Depends(get_comment_service)
):
    """Удаляет комментарий пользователя."""
    try:
        await service.delete_comment(comment_id, user.id)
    except DeletePostCommentError:
        raise HTTPException(
            400,
            "Comment cannot be deleted."
        )
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.patch(
    "/comments/{comment_id}/like",
    response_model=ReadCommentResponse
)
async def like_the_comment(
    comment_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: PostCommentService = Depends(get_comment_service)
) -> ReadCommentResponse:
    """Переключает лайк на комментарии."""
    try:
        return await service.toggle_comment_like(
            comment_id,
            user.id
        )
    except ReadPostCommentError:
        raise HTTPException(404,"Post not found")
    except ToggleCommentLikeError:
        raise HTTPException(400, "Like cannot be toggled.")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@comments_router.get(
    "/comments/{comment_id}/likes",
    response_model=List[CommentLikeResponse]
)
async def get_comment_likes(
    comment_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: PostCommentService = Depends(get_comment_service)
) -> List[CommentLikeResponse]:
    """Получает список лайков комментария."""
    try:
        likes = await service.get_comment_likes(
            comment_id,
            limit,
            offset
        )
    except ReadPostCommentError:
        raise HTTPException(404, "Comment not found")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return likes
