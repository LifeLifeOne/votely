from fastapi import FastAPI
from prometheus_client import REGISTRY, CollectorRegistry, Counter
from prometheus_fastapi_instrumentator import Instrumentator

# Business metric: votes actually recorded (a rejected vote is not counted).
VOTES = Counter("votely_votes_total", "Votes cast on polls.")

# Probes would drown the traffic figures, and the metrics page is not traffic.
EXCLUDED_HANDLERS = ["/healthz", "/readyz", "/metrics"]


def setup_metrics(app: FastAPI, registry: CollectorRegistry = REGISTRY) -> None:
    """Measure every request (count and duration per route template, so the number of series
    stays bounded) and serve them on /metrics. The frontend proxy only forwards /api/: the page
    is reachable from inside the cluster, where Prometheus reads it, not from the internet.

    One application per process uses the default registry; tests give each app its own."""
    Instrumentator(excluded_handlers=EXCLUDED_HANDLERS, registry=registry).instrument(app).expose(
        app, include_in_schema=False
    )
