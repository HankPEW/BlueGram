from src.api.posts.schemas import ReadPostResponse
from src.models import Post


class PostMapper:

    @staticmethod
    def to_response(post: Post) -> ReadPostResponse:

        return ReadPostResponse(
            id=post.post_id,
            title=post.title,
            body=post.body,
            author=post.user.login,
            created_at=post.created_at,
            likes_count=post.likes_count,
            comments_count=post.comments_count
        )