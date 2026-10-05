# syntax=docker/dockerfile:1

# ---- Build stage: resolve dependencies into a virtualenv with uv ----
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Dependencies first: this layer is cached as long as the lockfile does not change.
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-dev --no-install-project

# ---- Runtime stage: no build tools, no uv, non-root user ----
FROM python:3.12-slim AS runtime

# Apply Debian security fixes published after the base image was built.
RUN apt-get update \
 && apt-get upgrade -y --no-install-recommends \
 && rm -rf /var/lib/apt/lists/*

RUN groupadd --system --gid 10001 votely \
 && useradd --system --uid 10001 --gid votely --no-create-home votely

WORKDIR /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder /app/.venv /app/.venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

USER 10001:10001

EXPOSE 8000

# slim images have no curl: use Python itself for the container healthcheck.
HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=2)"]

# Behind a reverse proxy (nginx, ingress): trust X-Forwarded-* headers for client IP and scheme.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
