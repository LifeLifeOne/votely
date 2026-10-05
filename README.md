# Votely

[![English](https://img.shields.io/badge/lang-English-blue)](README.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](README.fr.md)

Votely is a lightweight polling application: create a poll, share it, collect votes (one per account) and follow the results live.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 · TypeScript · Vite · TanStack Query |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Database | PostgreSQL 16 |

## Repository layout

```
.
├── backend/        # REST API (FastAPI)
├── frontend/       # Web application (React)
├── compose.yaml    # Local development stack
└── docs/           # Technical documentation (en/, fr/)
```

## Getting started

Prerequisites: Docker, [mise](https://mise.jdx.dev/) (installs Python 3.12, uv and Node.js 24).

```bash
mise install                  # Python, uv and Node.js versions pinned in .mise.toml
cp .env.example .env          # then set a local password and a JWT secret (openssl rand -hex 32)
docker compose up -d db       # PostgreSQL on localhost:5432

cd backend
uv sync
set -a && . ../.env && set +a
uv run alembic upgrade head   # create the schema
uv run uvicorn app.main:app --reload
```

In another terminal:

```bash
cd frontend
npm ci
npm run dev                   # http://localhost:5173 (proxies /api to the backend)
```

- Application: http://localhost:5173
- API docs: http://localhost:8000/docs
- Liveness: `GET /healthz` · Readiness: `GET /readyz`

## Development

```bash
cd backend
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # format

cd frontend
npm test                # tests
npm run lint            # lint
npm run format          # format

uvx pre-commit install  # git hooks (lint + secret scanning)
```

## Documentation

- [Backend](docs/en/BACK.md): architecture, authentication, API, data model, migrations, tests
- [Frontend](docs/en/FRONT.md): architecture, API communication, user experience, tests

## License

[MIT](LICENSE)
