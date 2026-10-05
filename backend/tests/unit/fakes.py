import uuid
from datetime import UTC, datetime

from app.domain.errors import AlreadyVotedError, EmailAlreadyRegisteredError
from app.repositories.models import Poll, User


class InMemoryPollRepository:
    """Fake repository: same contract as SqlPollRepository, no database."""

    def __init__(self) -> None:
        self.polls: dict[uuid.UUID, Poll] = {}
        # (poll_id, option_id, user_id)
        self.votes: list[tuple[uuid.UUID, uuid.UUID, uuid.UUID]] = []

    def add(self, poll: Poll) -> Poll:
        # Mimic what the database does on insert: ids and timestamps.
        poll.id = uuid.uuid4()
        poll.created_at = datetime.now(UTC)
        for option in poll.options:
            option.id = uuid.uuid4()
        self.polls[poll.id] = poll
        return poll

    def get(self, poll_id: uuid.UUID) -> Poll | None:
        return self.polls.get(poll_id)

    def list_recent(self, limit: int, offset: int) -> list[Poll]:
        ordered = sorted(self.polls.values(), key=lambda p: p.created_at, reverse=True)
        return ordered[offset : offset + limit]

    def add_vote(self, poll_id: uuid.UUID, option_id: uuid.UUID, user_id: uuid.UUID) -> None:
        # Same rule as the unique constraint on (poll_id, user_id).
        if any(p == poll_id and u == user_id for p, _, u in self.votes):
            raise AlreadyVotedError()
        self.votes.append((poll_id, option_id, user_id))

    def voted_poll_ids(self, user_id: uuid.UUID, poll_ids: list[uuid.UUID]) -> set[uuid.UUID]:
        return {p for p, _, u in self.votes if u == user_id and p in poll_ids}

    def count_votes(self, poll_id: uuid.UUID) -> dict[uuid.UUID, int]:
        counts: dict[uuid.UUID, int] = {}
        for p, option_id, _ in self.votes:
            if p == poll_id:
                counts[option_id] = counts.get(option_id, 0) + 1
        return counts


class InMemoryUserRepository:
    def __init__(self) -> None:
        self.users: dict[uuid.UUID, User] = {}

    def add(self, user: User) -> User:
        if self.get_by_email(user.email) is not None:
            raise EmailAlreadyRegisteredError()
        user.id = uuid.uuid4()
        user.created_at = datetime.now(UTC)
        self.users[user.id] = user
        return user

    def get(self, user_id: uuid.UUID) -> User | None:
        return self.users.get(user_id)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.users.values() if u.email == email), None)
