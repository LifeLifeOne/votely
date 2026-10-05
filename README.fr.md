# Votely

[![English](https://img.shields.io/badge/lang-English-lightgrey)](README.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](README.fr.md)

Votely est une application de sondages légère : créer un sondage, le partager, recueillir des votes (un par compte) et suivre les résultats en direct.

## Stack

| Couche | Technologie |
|---|---|
| Frontend | React 19 · TypeScript · Vite · TanStack Query |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Base de données | PostgreSQL 16 |

## Organisation du dépôt

```
.
├── backend/        # API REST (FastAPI)
├── frontend/       # Application web (React)
├── compose.yaml    # Stack de développement local
└── docs/           # Documentation technique (en/, fr/)
```

## Démarrage

Prérequis : Docker, [mise](https://mise.jdx.dev/) (installe Python 3.12, uv et Node.js 24).

```bash
mise install                  # versions de Python, uv et Node.js fixées dans .mise.toml
cp .env.example .env          # puis définir un mot de passe local et un secret JWT (openssl rand -hex 32)
docker compose up -d db       # PostgreSQL sur localhost:5432

cd backend
uv sync
set -a && . ../.env && set +a
uv run alembic upgrade head   # création du schéma
uv run fastapi dev app/main.py
```

Dans un autre terminal :

```bash
cd frontend
npm ci
npm run dev                   # http://localhost:5173 (redirige /api vers le backend)
```

- Application : http://localhost:5173
- Documentation de l'API : http://localhost:8000/docs
- Liveness : `GET /healthz` · Readiness : `GET /readyz`

## Développement

```bash
cd backend
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # formatage

cd frontend
npm test                # tests
npm run lint            # lint
npm run format          # formatage

uvx pre-commit install  # hooks git (lint + détection de secrets)
```

## Documentation

- [Backend](docs/fr/BACK.md) : architecture, authentification, API, modèle de données, migrations, tests
- [Frontend](docs/fr/FRONT.md) : architecture, communication avec l'API, expérience utilisateur, tests

## Licence

[MIT](LICENSE)
