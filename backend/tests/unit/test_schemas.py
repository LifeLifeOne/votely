import pytest
from pydantic import ValidationError

from app.api.schemas import PollCreate


def test_question_and_options_are_trimmed():
    poll = PollCreate(question="  Best editor?  ", options=[" vim ", "emacs"])

    assert poll.question == "Best editor?"
    assert poll.options == ["vim", "emacs"]


@pytest.mark.parametrize(
    "options",
    [
        ["only one"],
        [f"option {i}" for i in range(11)],
        ["vim", "VIM"],
        ["vim", "   "],
    ],
    ids=["too-few", "too-many", "duplicates", "blank"],
)
def test_invalid_options_are_rejected(options):
    with pytest.raises(ValidationError):
        PollCreate(question="Best editor?", options=options)


def test_closing_date_requires_timezone():
    with pytest.raises(ValidationError):
        PollCreate(question="Best editor?", options=["a", "b"], closes_at="2030-01-01T10:00:00")
