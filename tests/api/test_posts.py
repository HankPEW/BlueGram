import pytest


def test_get_posts_list(client):
    response = client.get("/posts/")

    assert response.status_code == 200


def test_create_post_unauthorized(client):
    response = client.post(
        "/posts/",
        json={
            "title": "Test post",
            "body": "Test body"
        }
    )

    assert response.status_code == 401
