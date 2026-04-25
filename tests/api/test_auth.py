from random import randint


def test_login_wrong_credentials(client):
    response = client.post(
        "/login",
        json={
            "login": "wrong_user",
            "password": "wrong_password"
        }
    )

    assert response.status_code == 401


def test_register_user_success(client):
    response = client.post(
        "/register",
        json={
            "login": f"testuser{randint(1000,9999)}",
            "email": f"test{randint(1000,9999)}@example.com",
            "password": "Strongpassword1!",
            "repeated_password": "Strongpassword1!",
            "first_name": "Test",
            "last_name": "User",
            "gender": "male",
            "birth": "2000-01-01"
        }
    )

    assert response.status_code in (200,201)
