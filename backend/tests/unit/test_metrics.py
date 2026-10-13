import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY, CollectorRegistry

from app.api.deps import get_current_user
from app.api.polls import get_poll_service
from app.core.metrics import setup_metrics
from app.domain.errors import PollClosedError
from app.main import create_app
from app.repositories.models import User


def votes_total() -> float:
    return REGISTRY.get_sample_value("votely_votes_total") or 0.0


@pytest.fixture
def service():
    return MagicMock()


@pytest.fixture
def client(service):
    app = create_app()
    app.dependency_overrides[get_poll_service] = lambda: service
    app.dependency_overrides[get_current_user] = lambda: User(id=uuid.uuid4())
    return TestClient(app, raise_server_exceptions=False)


def cast_vote(client: TestClient):
    return client.post(f"/api/v1/polls/{uuid.uuid4()}/votes", json={"option_id": str(uuid.uuid4())})


def test_metrics_are_served_in_the_prometheus_format(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    assert "# TYPE votely_votes_total counter" in response.text


def test_a_recorded_vote_is_counted(client):
    before = votes_total()

    assert cast_vote(client).status_code == 204

    assert votes_total() == before + 1


def test_a_rejected_vote_is_not_counted(client, service):
    service.vote.side_effect = PollClosedError()
    before = votes_total()

    assert cast_vote(client).status_code >= 400

    assert votes_total() == before


def test_requests_are_counted_by_route_template_and_probes_are_left_out():
    app = FastAPI()

    @app.get("/items/{item_id}")
    def item(item_id: int) -> dict:
        return {}

    @app.get("/healthz")
    def health() -> dict:
        return {}

    setup_metrics(app, CollectorRegistry())
    client = TestClient(app)
    client.get("/items/1")
    client.get("/items/2")
    client.get("/healthz")

    text = client.get("/metrics").text

    assert 'handler="/items/{item_id}"' in text
    assert "/items/1" not in text
    assert 'handler="/healthz"' not in text
