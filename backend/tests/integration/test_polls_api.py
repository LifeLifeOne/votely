import uuid
from datetime import UTC, datetime, timedelta

import pytest

pytestmark = pytest.mark.integration


def create_poll(client, question="Best editor?", options=("vim", "emacs"), **extra):
    response = client.post(
        "/api/v1/polls", json={"question": question, "options": list(options), **extra}
    )
    assert response.status_code == 201, response.text
    return response.json()


def vote(client, poll, option_index=0):
    option_id = poll["options"][option_index]["id"]
    return client.post(f"/api/v1/polls/{poll['id']}/votes", json={"option_id": option_id})


def test_create_poll_records_its_author(auth_client):
    me = auth_client.get("/api/v1/auth/me").json()

    poll = create_poll(auth_client)

    assert poll["author_id"] == me["id"]


def test_polls_are_public_to_read(auth_client, client):
    created = create_poll(auth_client)

    response = client.get(f"/api/v1/polls/{created['id']}")

    assert response.status_code == 200
    poll = response.json()
    assert poll["question"] == "Best editor?"
    assert [option["label"] for option in poll["options"]] == ["vim", "emacs"]
    assert poll["is_closed"] is False
    assert client.get(f"/api/v1/polls/{created['id']}/results").status_code == 200


def test_anonymous_user_cannot_create_a_poll(client):
    response = client.post(
        "/api/v1/polls", json={"question": "Best editor?", "options": ["a", "b"]}
    )

    assert response.status_code == 401


def test_anonymous_user_cannot_vote(auth_client, client):
    poll = create_poll(auth_client)

    assert vote(client, poll).status_code == 401


def test_list_polls_newest_first_with_pagination(auth_client, client):
    for i in range(3):
        create_poll(auth_client, question=f"Question {i}")

    response = client.get("/api/v1/polls", params={"limit": 2})

    assert response.status_code == 200
    assert [poll["question"] for poll in response.json()] == ["Question 2", "Question 1"]


def test_votes_are_counted_in_results(auth_client, login_as):
    poll = create_poll(auth_client, options=("vim", "emacs", "vscode"))
    bob, carol = login_as("bob@example.com"), login_as("carol@example.com")
    for voter, option_index in ((auth_client, 0), (bob, 0), (carol, 1)):
        assert vote(voter, poll, option_index).status_code == 204

    results = auth_client.get(f"/api/v1/polls/{poll['id']}/results").json()

    assert results["total_votes"] == 3
    assert [(o["label"], o["votes"]) for o in results["options"]] == [
        ("vim", 2),
        ("emacs", 1),
        ("vscode", 0),
    ]


def test_unknown_poll_returns_404(client):
    response = client.get(f"/api/v1/polls/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "poll not found"}


def test_vote_for_option_of_another_poll_returns_422(auth_client):
    poll = create_poll(auth_client)
    other = create_poll(auth_client, question="Tabs or spaces?", options=("tabs", "spaces"))

    response = auth_client.post(
        f"/api/v1/polls/{poll['id']}/votes", json={"option_id": other["options"][0]["id"]}
    )

    assert response.status_code == 422


def test_invalid_payload_returns_422(auth_client):
    response = auth_client.post("/api/v1/polls", json={"question": "Q?", "options": ["only one"]})

    assert response.status_code == 422


def test_closing_date_in_the_past_returns_422(auth_client):
    yesterday = (datetime.now(UTC) - timedelta(days=1)).isoformat()

    response = auth_client.post(
        "/api/v1/polls",
        json={"question": "Best editor?", "options": ["vim", "emacs"], "closes_at": yesterday},
    )

    assert response.status_code == 422


def test_readiness_with_real_database(client):
    assert client.get("/readyz").status_code == 200
