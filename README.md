# Votely

[🇫🇷 Version française](README.fr.md)

Votely is a lightweight polling application: create a poll, share it, collect votes (one per account) and follow the results live.

## Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Database | PostgreSQL 16 |

## Repository layout

```
.
├── backend/        # REST API (FastAPI)
├── compose.yaml    # Local development stack
└── docs/           # Technical documentation
```

## Getting started

Prerequisites: Docker, [mise](https://mise.jdx.dev/) (installs Python 3.12 and uv).

```bash
mise install                  # Python + uv versions pinned in .mise.toml
cp .env.example .env          # then set a local password and a JWT secret (openssl rand -hex 32)
docker compose up -d db       # PostgreSQL on localhost:5432

cd backend
uv sync
set -a && . ../.env && set +a
uv run alembic upgrade head   # create the schema
uv run fastapi dev app/main.py
```

- API docs: http://localhost:8000/docs
- Liveness: `GET /healthz` · Readiness: `GET /readyz`

## Development

```bash
cd backend
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # format
uvx pre-commit install  # git hooks (lint + secret scanning)
```

## Documentation

- [Backend](docs/BACK.md): architecture, authentication, API, data model, migrations, tests

## License

[MIT](LICENSE)
