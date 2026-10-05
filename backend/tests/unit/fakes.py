import uuid
from datetime import UTC, datetime

from app.repositories.models import Poll


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
