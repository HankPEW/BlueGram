from src.api.comments.schemas import ReadCommentResponse
from src.models import PostComment


class CommentMapper:

    @staticmethod
    def to_response(comment: PostComment) -> ReadCommentResponse:
        return ReadCommentResponse(
            id=comment.comment_id,
            comment_text=comment.comment_text,
            author=comment.user.login,
            created_at=comment.created_at,
            likes_count=comment.likes_count
        )