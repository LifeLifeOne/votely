import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.repositories.models import Option, Poll, Vote


class SqlPollRepository:
    """PostgreSQL implementation of the poll repository."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, poll: Poll) -> Poll:
        self._session.add(poll)
        self._session.commit()
        self._session.refresh(poll)
        return poll

    def get(self, poll_id: uuid.UUID) -> Poll | None:
        return self._session.get(Poll, poll_id)

    def list_recent(self, limit: int, offset: int) -> list[Poll]:
        query = select(Poll).order_by(Poll.created_at.desc()).limit(limit).offset(offset)
        return list(self._session.scalars(query))

    def add_vote(self, option_id: uuid.UUID) -> None:
        self._session.add(Vote(option_id=option_id))
        self._session.commit()

    def count_votes(self, poll_id: uuid.UUID) -> dict[uuid.UUID, int]:
        query = (
            select(Vote.option_id, func.count(Vote.id))
            .join(Option, Option.id == Vote.option_id)
            .where(Option.poll_id == poll_id)
            .group_by(Vote.option_id)
        )
        return {option_id: count for option_id, count in self._session.execute(query).all()}
