from datetime import timedelta

from app.core.security import create_access_token, decode_access_token

SECRET = "unit-test-secret-" + "x" * 32


def test_token_round_trip():
    token = create_access_token("user-42", SECRET, timedelta(minutes=5))

    assert decode_access_token(token, SECRET) == "user-42"


def test_expired_token_is_rejected():
    token = create_access_token("user-42", SECRET, timedelta(seconds=-1))

    assert decode_access_token(token, SECRET) is None


def test_token_signed_with_another_secret_is_rejected():
    token = create_access_token("user-42", "another-secret-" + "y" * 32, timedelta(minutes=5))

    assert decode_access_token(token, SECRET) is None


def test_garbage_token_is_rejected():
    assert decode_access_token("not-a-jwt", SECRET) is None
