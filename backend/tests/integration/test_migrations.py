import uuid

import pytest
from alembic import command
from sqlalchemy import text

from tests.integration.conftest import alembic_config

pytestmark = pytest.mark.integration

BEFORE_ONE_VOTE_PER_USER = "0810e36df54b"


def test_existing_votes_survive_the_one_vote_per_user_migration(engine):
    config = alembic_config(engine.url.render_as_string(hide_password=False))
    command.downgrade(config, BEFORE_ONE_VOTE_PER_USER)
    poll_id, option_id = uuid.uuid4(), uuid.uuid4()
    try:
        with engine.begin() as connection:
            connection.execute(
                text("INSERT INTO polls (id, question) VALUES (:id, 'Legacy poll?')"),
                {"id": poll_id},
            )
            connection.execute(
                text(
                    "INSERT INTO options (id, poll_id, label, position) VALUES (:id, :poll, 'A', 0)"
                ),
                {"id": option_id, "poll": poll_id},
            )
            # Anonymous votes, as cast before accounts existed.
            connection.execute(
                text("INSERT INTO votes (option_id) VALUES (:option), (:option)"),
                {"option": option_id},
            )

        command.upgrade(config, "head")

        with engine.connect() as connection:
            rows = connection.execute(text("SELECT poll_id, user_id FROM votes")).all()
        assert rows == [(poll_id, None), (poll_id, None)]
    finally:
        command.upgrade(config, "head")
