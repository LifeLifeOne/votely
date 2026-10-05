from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


@lru_cache
def get_engine() -> Engine:
    # pool_pre_ping drops dead connections, e.g. after a database restart.
    return create_engine(get_settings().database_url, pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """FastAPI dependency yielding one database session per request."""
    session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    with session_factory() as session:
        yield session
