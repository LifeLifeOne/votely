import pytest
from pydantic import ValidationError

from app.core.config import Settings


def test_short_jwt_secret_is_refused():
    with pytest.raises(ValidationError):
        Settings(jwt_secret="too-short")


def test_cookies_are_secure_by_default(monkeypatch):
    monkeypatch.delenv("VOTELY_COOKIE_SECURE", raising=False)

    assert Settings(_env_file=None, jwt_secret="x" * 32).cookie_secure is True
