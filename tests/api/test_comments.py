import pytest


def test_get_comments_for_post(client):
    response = client.get("/1/comments")

    assert response.status_code in (200, 404)


def test_create_comment_unauthorized(client):
    response = client.post(
        "/comments",
        params={"post_id": 1},
        json={
            "comment_text": "Test comment"
        }
    )

    assert response.status_code == 401