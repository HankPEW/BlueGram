from src.api.comments.schemas import CommentLikeResponse
from src.models import CommentLike


class CommentLikeMapper:
    @staticmethod
    def to_response(like: CommentLike) -> CommentLikeResponse:
        return CommentLikeResponse(
            user_id=like.user.user_id,
            login=like.user.login
        )

    @staticmethod
    def list_to_response(likes: list[CommentLike]) -> list[CommentLikeResponse]:
        return [CommentLikeMapper.to_response(like) for like in likes]