from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import CurrentUser
from src.api.posts.schemas import (
    CreatePostRequest,
    ReadPostResponse,
    UpdatePostRequest,
    PostLikeResponse
)
from src.repositories.exceptions import RepositoryError
from src.services import PostService
from src.services.dependencies.post import get_post_service
from src.services.exceptions import (
    AddPostError,
    DeletePostError,
    ReadPostError,
    TogglePostLikeError,
    UpdatePostError

)


posts_router = APIRouter(prefix="/posts", tags=["Posts"])


@posts_router.get(
    "/",
    response_model=List[ReadPostResponse]
)
async def read_posts(
    service: PostService = Depends(get_post_service),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> List[ReadPostResponse]:
    """Получает список постов с пагинацией."""
    try:
        return await service.read_all_posts(limit, offset)
    except ReadPostError:
        raise HTTPException(404, "Post not found.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.get(
    "/{post_id}",
    response_model=ReadPostResponse
)
async def read_post(
    post_id: int,
    service: PostService = Depends(get_post_service)
) -> ReadPostResponse:
    """Получает пост по его идентификатору."""
    try:
        return await service.read_post(post_id)
    except ReadPostError:
        raise HTTPException(404, "Post not found")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.post(
    "/",
    response_model=ReadPostResponse
)
async def create_post(
    data: CreatePostRequest,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
) -> ReadPostResponse | None:
    """Создаёт новый пост."""
    try:
        return await service.create_post(data, user.id)
    except AddPostError:
        raise HTTPException(404, "Post cannot be created")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch(
    "/{post_id}",
    response_model=ReadPostResponse
)
async def update_post(
    data: UpdatePostRequest,
    post_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
) -> ReadPostResponse:
    """Обновляет существующий пост."""
    try:
        return await service.update_post(data, post_id, user.id)
    except UpdatePostError:
        raise HTTPException(404, "Post cannot be updated")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.delete("/{post_id}", status_code=204)
async def delete_post(
    post_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
):
    """Удаляет пост."""
    try:
        await service.delete_post(post_id, user.id)
    except DeletePostError:
        raise HTTPException(404, "Post cannot be deleted")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch(
    "/{post_id}/like",
    response_model=ReadPostResponse
)
async def like_the_post(
    post_id: int,
    user: CurrentUser = Depends(get_current_user),
    service: PostService = Depends(get_post_service)
) -> ReadPostResponse:
    """Переключает лайк поста (добавить/убрать)."""
    try:
        return await service.toggle_post_like(post_id, user.id)
    except ReadPostError:
        raise HTTPException(404,"Post not found")
    except TogglePostLikeError:
        raise HTTPException(400, "Like cannot be toggled.")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )


@posts_router.get(
    "/{post_id}/likes",
    response_model=List[PostLikeResponse]
)
async def get_post_likes(
    post_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: PostService = Depends(get_post_service)
) -> List[PostLikeResponse]:
    """Получает список лайков поста."""
    try:
        post_likes = await service.get_post_likes(post_id, limit, offset)
    except ReadPostError:
        raise HTTPException(404, "Post not found")
    except RepositoryError:
        raise HTTPException(
            500,
            "An internal server error occurred."
        )

    return post_likes
