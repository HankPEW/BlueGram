from src.api.comments.schemas import CommentLikeResponse
from src.models import CommentLike


class CommentLikeMapper:
    """Маппер для преобразования лайков комментариев в response-схемы."""

    @staticmethod
    def to_response(like: CommentLike) -> CommentLikeResponse:
        """Преобразует лайк комментария в CommentLikeResponse."""
        return CommentLikeResponse(
            user_id=like.user.user_id,
            login=like.user.login
        )

    @staticmethod
    def list_to_response(
        likes: list[CommentLike]) -> list[CommentLikeResponse]:
        """Преобразует список лайков в список response-схем."""
        return [
            CommentLikeMapper.to_response(like)
            for like in likes
        ]