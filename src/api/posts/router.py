from typing import List
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends, Query

from src.api.auth.dependencies import get_current_user
from src.api.auth.schemas import CurrentUser
from src.api.comments.comment_like_mapper import CommentLikeMapper
from src.api.posts.post_likes_mapper import PostLikeMapper
from src.api.posts.schemas import ReadPostResponse, UpdatePostRequest, CreatePostRequest, PostLikeResponse
from src.api.comments.schemas import ReadCommentResponse, CreateCommentRequest, UpdateCommentRequest, \
    CommentLikeResponse
from src.datebase.dependencies import get_uow
from src.repositories.exceptions import  RepositoryError
from src.services import PostCommentService, PostService
from src.services.exceptions import AddPostError, ReadPostError, UpdatePostError, DeletePostError, \
    ReadPostCommentError, AddPostCommentError, UpdatePostCommentError, DeletePostCommentError, \
 TogglePostLikeError, ToggleCommentLikeError
from src.datebase.dbmanager import DBManager


posts_router = APIRouter(prefix="/posts")


@posts_router.get("/", response_model=List[ReadPostResponse])
async def read_posts(
    uow: DBManager = Depends(get_uow),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    service = PostService(uow)
    try:
        return await service.read_all_posts(limit, offset)
    except ReadPostError:
        raise HTTPException(404, "Post not found.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.get("/{post_id}", response_model=ReadPostResponse)
async def read_post(post_id: int, uow: DBManager = Depends(get_uow)):
    service = PostService(uow)
    try:
        return await service.read_post(post_id)
    except ReadPostError:
        raise HTTPException(404, "Post not found")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.post("/", response_model=ReadPostResponse)
async def create_post(
    data: CreatePostRequest,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostService(uow)
    try:
        return await service.create_post(data, user.id)
    except AddPostError:
        HTTPException(404, "Post cannot be created")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch("/{post_id}", response_model=ReadPostResponse)
async def update_post(
    data: UpdatePostRequest,
    post_id: int,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostService(uow)
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
    uow: DBManager = Depends(get_uow)
):
    service = PostService(uow)
    try:
        await service.delete_post(post_id, user.id)
    except DeletePostError:
        raise HTTPException(404, "Post cannot be deleted")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch("/{post_id}/like", response_model=ReadPostResponse)
async def like_the_post(
    post_id: int,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostService(uow)
    try:
        return await service.toggle_post_like(post_id, user.id)
    except ReadPostError:
        raise HTTPException(404,"Post not found")
    except TogglePostLikeError:
        raise HTTPException(400, "Like cannot be toggled.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.get("/posts/{post_id}/likes", response_model=List[PostLikeResponse])
async def get_post_likes(
    post_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow: DBManager = Depends(get_uow)
):
    service = PostService(uow)
    try:
        post_likes = await service.get_post_likes(post_id, limit, offset)
    except ReadPostError:
        raise HTTPException(404, "Post not found")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")

    return PostLikeMapper.list_to_response(post_likes)

###### РОУТЕР СДЕЛАЙ ОТДЕЛЬНЫЙ ДЛЯ КОММЕНТОВ!!!!!

@posts_router.get("/{post_id}/comments", response_model=List[ReadCommentResponse])
async def read_comments(
    post_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        return await service.read_post_comments(post_id, limit, offset)
    except ReadPostCommentError:
        raise HTTPException(404, "Comments not found.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.get("/comments/{comment_id}", response_model=ReadCommentResponse)
async def read_comment(comment_id: int, uow: DBManager = Depends(get_uow)):
    service = PostCommentService(uow)
    try:
        return await service.read_comment(comment_id)
    except ReadPostCommentError:
        raise HTTPException(404, "Comment not found.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.post("/comments", response_model=ReadCommentResponse)
async def create_comment(
    post_id: int,
    data: CreateCommentRequest,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        return await service.create_comment(data, post_id, user.id)
    except AddPostCommentError:
        raise HTTPException(400, "Comment cannot be created.")
    except ReadPostCommentError:
        raise HTTPException(404, "Comments not found.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch("/comments/{comment_id}", response_model=ReadCommentResponse)
async def update_comment(
    comment_id: int,
    data: UpdateCommentRequest,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        return await service.update_comment(data, user.id, comment_id)
    except UpdatePostCommentError:
        raise HTTPException(400, "Comment cannot be updated.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.delete("/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: int,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        await service.delete_comment(comment_id, user.id)
    except DeletePostCommentError:
        raise HTTPException(400, "Comment cannot be deleted.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.patch("/comments/{comment_id}/like", response_model=ReadCommentResponse)
async def like_the_comment(
    comment_id: int,
    user: CurrentUser = Depends(get_current_user),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        return await service.toggle_comment_like(comment_id, user.id)
    except ReadPostCommentError:
        raise HTTPException(404,"Post not found")
    except ToggleCommentLikeError:
        raise HTTPException(400, "Like cannot be toggled.")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")


@posts_router.get("/comments/{comment_id}/likes", response_model=List[CommentLikeResponse])
async def get_comment_likes(
    comment_id: int,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    uow: DBManager = Depends(get_uow)
):
    service = PostCommentService(uow)
    try:
        likes = await service.get_comment_likes(comment_id, limit, offset)
    except ReadPostCommentError:
        raise HTTPException(404, "Comment not found")
    except RepositoryError:
        raise HTTPException(500, "An internal server error occurred.")

    return CommentLikeMapper.list_to_response(likes)

