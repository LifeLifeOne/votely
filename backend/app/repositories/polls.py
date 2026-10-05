import uuid

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.domain.errors import AlreadyVotedError
from app.repositories.models import Poll, Vote

ONE_VOTE_PER_USER = "uq_votes_poll_id_user_id"


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

    def add_vote(self, poll_id: uuid.UUID, option_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self._session.add(Vote(poll_id=poll_id, option_id=option_id, user_id=user_id))
        try:
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            if getattr(exc.orig.diag, "constraint_name", None) == ONE_VOTE_PER_USER:
                raise AlreadyVotedError() from exc
            raise

    def voted_poll_ids(self, user_id: uuid.UUID, poll_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        query = select(Vote.poll_id).where(Vote.user_id == user_id, Vote.poll_id.in_(poll_ids))
        return set(self._session.scalars(query))

    def count_votes(self, poll_id: uuid.UUID) -> dict[uuid.UUID, int]:
        query = (
            select(Vote.option_id, func.count(Vote.id))
            .where(Vote.poll_id == poll_id)
            .group_by(Vote.option_id)
        )
        return {option_id: count for option_id, count in self._session.execute(query).all()}
