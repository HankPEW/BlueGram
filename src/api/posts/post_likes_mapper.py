from src.api.posts.schemas import PostLikeResponse
from src.models import PostLike


class PostLikeMapper:
    """Маппер для преобразования лайков постов в response-схемы."""

    @staticmethod
    def to_response(like: PostLike) -> PostLikeResponse:
        """Преобразует лайк поста в PostLikeResponse."""
        return PostLikeResponse(
            user_id=like.user.user_id,
            login=like.user.login
        )

    @staticmethod
    def list_to_response(
        likes: list[PostLike]
    ) -> list[PostLikeResponse]:
        """Преобразует список лайков в список response-схем."""
        return [
            PostLikeMapper.to_response(like)
            for like in likes
        ]
