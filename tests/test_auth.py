import pytest


def login(client, username="rahul", password="test-password"):
    return client.post("/api/auth/login", json={"username": username, "password": password})


def test_valid_login_and_me(client):
    assert login(client).status_code == 200
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json["user"] == {"username": "rahul", "name": "Rahul", "role": "student"}


def test_invalid_login(client):
    assert login(client, password="wrong").status_code == 401


def test_logout_clears_session(client):
    login(client)
    assert client.post("/api/auth/logout").status_code == 200
    assert client.get("/api/auth/me").status_code == 401


@pytest.mark.parametrize("username,role", [("rahul", "student"), ("mrs-sharma", "parent"), ("mr-patil", "teacher"), ("dr-deshmukh", "principal")])
def test_all_demo_roles_can_log_in(client, username, role):
    response = login(client, username)
    assert response.status_code == 200
    assert response.json["user"]["role"] == role
