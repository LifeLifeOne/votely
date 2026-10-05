# Votely

[![English](https://img.shields.io/badge/lang-English-lightgrey)](README.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](README.fr.md)

Votely est une application de sondages légère : créer un sondage, le partager, recueillir des votes (un par compte) et suivre les résultats en direct.

## Stack

| Couche | Technologie |
|---|---|
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Base de données | PostgreSQL 16 |

## Organisation du dépôt

```
.
├── backend/        # API REST (FastAPI)
├── compose.yaml    # Stack de développement local
└── docs/           # Documentation technique (en/, fr/)
```

## Démarrage

Prérequis : Docker, [mise](https://mise.jdx.dev/) (installe Python 3.12 et uv).

```bash
mise install                  # versions de Python et uv fixées dans .mise.toml
cp .env.example .env          # puis définir un mot de passe local et un secret JWT (openssl rand -hex 32)
docker compose up -d db       # PostgreSQL sur localhost:5432

cd backend
uv sync
set -a && . ../.env && set +a
uv run alembic upgrade head   # création du schéma
uv run fastapi dev app/main.py
```

- Documentation de l'API : http://localhost:8000/docs
- Liveness : `GET /healthz` · Readiness : `GET /readyz`

## Développement

```bash
cd backend
uv run pytest           # tests
uv run ruff check .     # lint
uv run ruff format .    # formatage
uvx pre-commit install  # hooks git (lint + détection de secrets)
```

## Documentation

- [Backend](docs/fr/BACK.md) : architecture, authentification, API, modèle de données, migrations, tests

## Licence

[MIT](LICENSE)
