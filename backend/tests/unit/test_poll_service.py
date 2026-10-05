import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.domain.errors import (
    AlreadyVotedError,
    InvalidClosingDateError,
    OptionNotFoundError,
    PollClosedError,
    PollNotFoundError,
)
from app.domain.polls import PollService
from tests.unit.fakes import InMemoryPollRepository

NOW = datetime(2026, 1, 1, 12, 0, tzinfo=UTC)
AUTHOR = uuid.uuid4()
VOTER = uuid.uuid4()


@pytest.fixture
def repository() -> InMemoryPollRepository:
    return InMemoryPollRepository()


@pytest.fixture
def service(repository) -> PollService:
    return PollService(repository, clock=lambda: NOW)


def test_create_poll_keeps_option_order_and_author(service):
    poll = service.create_poll("Best editor?", ["vim", "emacs", "vscode"], AUTHOR)

    assert poll.author_id == AUTHOR
    assert [option.label for option in poll.options] == ["vim", "emacs", "vscode"]
    assert [option.position for option in poll.options] == [0, 1, 2]


def test_create_poll_rejects_closing_date_in_the_past(service):
    with pytest.raises(InvalidClosingDateError):
        service.create_poll(
            "Best editor?", ["vim", "emacs"], AUTHOR, closes_at=NOW - timedelta(days=1)
        )


def test_get_unknown_poll_raises(service):
    with pytest.raises(PollNotFoundError):
        service.get_poll(uuid.uuid4())


def test_vote_is_recorded(service, repository):
    poll = service.create_poll("Best editor?", ["vim", "emacs"], AUTHOR)

    service.vote(poll.id, poll.options[0].id, VOTER)

    assert repository.votes == [(poll.id, poll.options[0].id, VOTER)]


def test_second_vote_of_the_same_user_is_rejected(service):
    poll = service.create_poll("Best editor?", ["vim", "emacs"], AUTHOR)
    service.vote(poll.id, poll.options[0].id, VOTER)

    with pytest.raises(AlreadyVotedError):
        service.vote(poll.id, poll.options[1].id, VOTER)


def test_voted_poll_ids_only_lists_polls_the_user_voted_on(service):
    voted = service.create_poll("Best editor?", ["vim", "emacs"], AUTHOR)
    not_voted = service.create_poll("Tabs or spaces?", ["tabs", "spaces"], AUTHOR)
    service.vote(voted.id, voted.options[0].id, VOTER)

    assert service.voted_poll_ids(VOTER, [voted, not_voted]) == {voted.id}
    assert service.voted_poll_ids(None, [voted, not_voted]) == set()


def test_vote_with_option_from_another_poll_is_rejected(service):
    poll = service.create_poll("Best editor?", ["vim", "emacs"], AUTHOR)
    other = service.create_poll("Tabs or spaces?", ["tabs", "spaces"], AUTHOR)

    with pytest.raises(OptionNotFoundError):
        service.vote(poll.id, other.options[0].id, VOTER)


def test_vote_on_closed_poll_is_rejected(repository):
    poll = PollService(repository, clock=lambda: NOW).create_poll(
        "Best editor?", ["vim", "emacs"], AUTHOR, closes_at=NOW + timedelta(hours=1)
    )
    later = PollService(repository, clock=lambda: NOW + timedelta(hours=2))

    with pytest.raises(PollClosedError):
        later.vote(poll.id, poll.options[0].id, VOTER)


def test_results_count_votes_and_percentages(service):
    poll = service.create_poll("Best editor?", ["vim", "emacs", "vscode"], AUTHOR)
    vim, emacs, vscode = poll.options
    for option in (vim, vim, emacs):
        service.vote(poll.id, option.id, uuid.uuid4())

    results = service.get_results(poll.id)

    assert results.total_votes == 3
    assert [(r.label, r.votes, r.percentage) for r in results.options] == [
        ("vim", 2, 66.7),
        ("emacs", 1, 33.3),
        ("vscode", 0, 0.0),
    ]


def test_results_without_votes(service):
    poll = service.create_poll("Best editor?", ["vim", "emacs"], AUTHOR)

    results = service.get_results(poll.id)

    assert results.total_votes == 0
    assert all(r.percentage == 0.0 for r in results.options)
