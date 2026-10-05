import os
from collections.abc import Callable, Iterator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import Engine, create_engine, make_url, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.core.db import get_session
from app.main import create_app

BACKEND_DIR = Path(__file__).resolve().parents[2]


def resolve_test_database_url() -> str:
    """Dedicated database next to the dev one (votely -> votely_test)."""
    if url := os.getenv("VOTELY_TEST_DATABASE_URL"):
        return url
    dev_url = make_url(get_settings().database_url)
    return dev_url.set(database=f"{dev_url.database}_test").render_as_string(hide_password=False)


def ensure_database_exists(url: str) -> None:
    target = make_url(url)
    admin = create_engine(target.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        exists = connection.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"), {"name": target.database}
        )
        if not exists:
            connection.execute(text(f'CREATE DATABASE "{target.database}"'))
    admin.dispose()


def alembic_config(url: str) -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", url.replace("%", "%%"))
    return config


@pytest.fixture(scope="session")
def engine() -> Iterator[Engine]:
    url = resolve_test_database_url()
    try:
        ensure_database_exists(url)
    except OperationalError as exc:
        # Locally, allow running unit tests without PostgreSQL. In CI, never skip silently.
        if os.getenv("CI"):
            raise
        pytest.skip(f"PostgreSQL unavailable, start it with 'docker compose up -d db' ({exc})")

    # Build the schema through the real migrations, so they are tested too.
    command.upgrade(alembic_config(url), "head")

    engine = create_engine(url)
    yield engine
    engine.dispose()


@pytest.fixture
def session(engine) -> Iterator[Session]:
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        yield session
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE users, polls, options, votes RESTART IDENTITY CASCADE"))


PASSWORD = "correct horse battery"


@pytest.fixture
def app(session) -> FastAPI:
    app = create_app()
    app.dependency_overrides[get_session] = lambda: session
    return app


@pytest.fixture
def client(app) -> TestClient:
    """Anonymous client."""
    return TestClient(app)


@pytest.fixture
def login_as(app) -> Callable[[str], TestClient]:
    """Return a factory creating a client logged in as a freshly registered user."""

    def _login_as(email: str) -> TestClient:
        client = TestClient(app)
        credentials = {"email": email, "password": PASSWORD}
        assert client.post("/api/v1/auth/register", json=credentials).status_code == 201
        assert client.post("/api/v1/auth/login", json=credentials).status_code == 204
        return client

    return _login_as


@pytest.fixture
def auth_client(login_as) -> TestClient:
    return login_as("alice@example.com")
