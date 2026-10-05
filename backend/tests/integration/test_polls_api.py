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


def test_create_and_get_poll(client):
    created = create_poll(client)

    response = client.get(f"/api/v1/polls/{created['id']}")

    assert response.status_code == 200
    poll = response.json()
    assert poll["question"] == "Best editor?"
    assert [option["label"] for option in poll["options"]] == ["vim", "emacs"]
    assert poll["is_closed"] is False


def test_list_polls_newest_first_with_pagination(client):
    for i in range(3):
        create_poll(client, question=f"Question {i}")

    response = client.get("/api/v1/polls", params={"limit": 2})

    assert response.status_code == 200
    assert [poll["question"] for poll in response.json()] == ["Question 2", "Question 1"]


def test_vote_then_read_results(client):
    poll = create_poll(client, options=("vim", "emacs", "vscode"))
    vim, emacs, _ = (option["id"] for option in poll["options"])
    for option_id in (vim, vim, emacs):
        response = client.post(f"/api/v1/polls/{poll['id']}/votes", json={"option_id": option_id})
        assert response.status_code == 204

    results = client.get(f"/api/v1/polls/{poll['id']}/results").json()

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


def test_vote_for_option_of_another_poll_returns_422(client):
    poll = create_poll(client)
    other = create_poll(client, question="Tabs or spaces?", options=("tabs", "spaces"))

    response = client.post(
        f"/api/v1/polls/{poll['id']}/votes", json={"option_id": other["options"][0]["id"]}
    )

    assert response.status_code == 422


def test_invalid_payload_returns_422(client):
    response = client.post("/api/v1/polls", json={"question": "Q?", "options": ["only one"]})

    assert response.status_code == 422


def test_closing_date_in_the_past_returns_422(client):
    yesterday = (datetime.now(UTC) - timedelta(days=1)).isoformat()

    response = client.post(
        "/api/v1/polls",
        json={"question": "Best editor?", "options": ["vim", "emacs"], "closes_at": yesterday},
    )

    assert response.status_code == 422


def test_readiness_with_real_database(client):
    assert client.get("/readyz").status_code == 200
