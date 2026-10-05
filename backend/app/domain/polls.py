import uuid
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from app.domain.errors import (
    InvalidClosingDateError,
    OptionNotFoundError,
    PollClosedError,
    PollNotFoundError,
)
from app.repositories.models import Option, Poll


class PollRepository(Protocol):
    """Persistence port used by the service; lets unit tests swap in a fake."""

    def add(self, poll: Poll) -> Poll: ...
    def get(self, poll_id: uuid.UUID) -> Poll | None: ...
    def list_recent(self, limit: int, offset: int) -> list[Poll]: ...
    def add_vote(self, option_id: uuid.UUID) -> None: ...
    def count_votes(self, poll_id: uuid.UUID) -> dict[uuid.UUID, int]: ...


@dataclass(frozen=True)
class OptionResult:
    option_id: uuid.UUID
    label: str
    votes: int
    percentage: float


@dataclass(frozen=True)
class PollResults:
    poll_id: uuid.UUID
    total_votes: int
    options: list[OptionResult]


def utc_now() -> datetime:
    return datetime.now(UTC)


def is_closed(poll: Poll, now: datetime) -> bool:
    return poll.closes_at is not None and poll.closes_at <= now


class PollService:
    """Business rules for polls. Input shape (lengths, option count) is validated
    by the API schemas; rules that depend on time or stored data live here."""

    def __init__(self, repository: PollRepository, clock: Callable[[], datetime] = utc_now):
        self._repository = repository
        self._clock = clock

    def create_poll(
        self, question: str, option_labels: list[str], closes_at: datetime | None = None
    ) -> Poll:
        if closes_at is not None and closes_at <= self._clock():
            raise InvalidClosingDateError()

        options = [
            Option(label=label, position=position) for position, label in enumerate(option_labels)
        ]
        return self._repository.add(Poll(question=question, closes_at=closes_at, options=options))

    def list_polls(self, limit: int, offset: int) -> list[Poll]:
        return self._repository.list_recent(limit=limit, offset=offset)

    def get_poll(self, poll_id: uuid.UUID) -> Poll:
        poll = self._repository.get(poll_id)
        if poll is None:
            raise PollNotFoundError()
        return poll

    def vote(self, poll_id: uuid.UUID, option_id: uuid.UUID) -> None:
        poll = self.get_poll(poll_id)
        if is_closed(poll, self._clock()):
            raise PollClosedError()
        if option_id not in {option.id for option in poll.options}:
            raise OptionNotFoundError()
        self._repository.add_vote(option_id)

    def get_results(self, poll_id: uuid.UUID) -> PollResults:
        poll = self.get_poll(poll_id)
        counts = self._repository.count_votes(poll_id)
        total = sum(counts.values())

        return PollResults(
            poll_id=poll.id,
            total_votes=total,
            options=[
                OptionResult(
                    option_id=option.id,
                    label=option.label,
                    votes=counts.get(option.id, 0),
                    percentage=round(100 * counts.get(option.id, 0) / total, 1) if total else 0.0,
                )
                for option in poll.options
            ],
        )
