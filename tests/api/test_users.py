from fastapi import status


def test_get_user_profile_not_found(client):
    response = client.get("/profile/999999")

    assert response.status_code == 404


def test_get_my_profile_unauthorized(client):
    response = client.get("/profile/me")

    assert response.status_code == 401
