from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.db import get_session
from app.main import create_app


@pytest.fixture
def app():
    return create_app()


def override_session(session: MagicMock):
    def _get_session() -> Iterator[MagicMock]:
        yield session

    return _get_session


def test_liveness_is_ok(app):
    response = TestClient(app).get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_when_database_answers(app):
    app.dependency_overrides[get_session] = override_session(MagicMock())

    response = TestClient(app).get("/readyz")

    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_readiness_when_database_is_down(app):
    session = MagicMock()
    session.execute.side_effect = OperationalError("SELECT 1", {}, Exception("down"))
    app.dependency_overrides[get_session] = override_session(session)

    response = TestClient(app).get("/readyz")

    assert response.status_code == 503
    assert response.json() == {"detail": "database unavailable"}
