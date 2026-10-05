import uuid
from datetime import UTC, datetime

from app.domain.errors import EmailAlreadyRegisteredError
from app.repositories.models import Poll, User


class InMemoryPollRepository:
    """Fake repository: same contract as SqlPollRepository, no database."""

    def __init__(self) -> None:
        self.polls: dict[uuid.UUID, Poll] = {}
        self.votes: list[uuid.UUID] = []

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

    def add_vote(self, option_id: uuid.UUID) -> None:
        self.votes.append(option_id)

    def count_votes(self, poll_id: uuid.UUID) -> dict[uuid.UUID, int]:
        option_ids = {option.id for option in self.polls[poll_id].options}
        counts: dict[uuid.UUID, int] = {}
        for option_id in self.votes:
            if option_id in option_ids:
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
