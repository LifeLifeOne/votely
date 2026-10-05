import pytest

pytestmark = pytest.mark.integration

PASSWORD = "correct horse battery"


def register(client, email="alice@example.com", password=PASSWORD):
    return client.post("/api/v1/auth/register", json={"email": email, "password": password})


def login(client, email="alice@example.com", password=PASSWORD):
    return client.post("/api/v1/auth/login", json={"email": email, "password": password})


def test_register_returns_user_without_password(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert "password" not in body and "password_hash" not in body


def test_register_twice_returns_409(client):
    register(client)

    assert register(client, email="ALICE@example.com").status_code == 409


@pytest.mark.parametrize(
    ("email", "password"),
    [("not-an-email", PASSWORD), ("alice@example.com", "too short")],
    ids=["invalid-email", "short-password"],
)
def test_register_with_invalid_payload_returns_422(client, email, password):
    assert register(client, email=email, password=password).status_code == 422


def test_login_sets_a_secure_session_cookie(client):
    register(client)

    response = login(client)

    assert response.status_code == 204
    cookie = response.headers["set-cookie"].lower()
    assert "votely_session=" in cookie
    assert "httponly" in cookie
    assert "samesite=lax" in cookie


def test_me_after_login(client):
    register(client)
    login(client)

    response = client.get("/api/v1/auth/me")

    assert response.status_code == 200
    assert response.json()["email"] == "alice@example.com"


def test_me_without_session_returns_401(client):
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_with_tampered_cookie_returns_401(client):
    client.cookies.set("votely_session", "forged.token.value")

    assert client.get("/api/v1/auth/me").status_code == 401


def test_logout_ends_the_session(client):
    register(client)
    login(client)

    assert client.post("/api/v1/auth/logout").status_code == 204
    assert client.get("/api/v1/auth/me").status_code == 401


@pytest.mark.parametrize(
    ("email", "password"),
    [("alice@example.com", "wrong password!!"), ("nobody@example.com", PASSWORD)],
    ids=["wrong-password", "unknown-email"],
)
def test_login_failures_return_the_same_401(client, email, password):
    register(client)

    response = login(client, email=email, password=password)

    assert response.status_code == 401
    assert response.json() == {"detail": "invalid email or password"}
