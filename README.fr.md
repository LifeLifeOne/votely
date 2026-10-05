# Votely

[![English](https://img.shields.io/badge/lang-English-lightgrey)](README.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-blue)](README.fr.md) [![pipeline](https://gitlab.com/StateOfFlowHunter/votely/badges/main/pipeline.svg)](https://gitlab.com/StateOfFlowHunter/votely/-/pipelines)

Votely est une application de sondages légère : créer un sondage, le partager, recueillir des votes (un par compte) et suivre les résultats en direct.

## Stack

| Couche | Technologie |
|---|---|
| Frontend | React 19 · TypeScript · Vite · TanStack Query |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Base de données | PostgreSQL 16 |
| Conteneurs | Images Docker multi-étapes · nginx · Docker Compose |
| Tests | pytest · Vitest · Testing Library · MSW · Playwright |

## Organisation du dépôt

```
.
├── backend/          # API REST (FastAPI)
├── e2e/              # Tests end-to-end (Playwright)
├── frontend/         # Application web (React)
├── compose.yaml      # Stack complète (Docker Compose)
├── compose.e2e.yaml  # Stack jetable pour les tests end-to-end
└── docs/             # Documentation technique (en/, fr/)
```

## Démarrage

### Lancer toute la stack avec Docker

```bash
cp .env.example .env          # puis définir un mot de passe de base et un secret JWT (openssl rand -hex 32)
docker compose up --build     # http://localhost:8080
```

### Développement local

Prérequis : Docker, [mise](https://mise.jdx.dev/) (installe Python 3.12, uv et Node.js 24).

```bash
mise install                  # versions de Python, uv et Node.js fixées dans .mise.toml
cp .env.example .env          # puis définir un mot de passe local et un secret JWT (openssl rand -hex 32)
docker compose up -d db       # PostgreSQL sur localhost:5432

cd backend
uv sync
set -a && . ../.env && set +a
uv run alembic upgrade head   # création du schéma
uv run uvicorn app.main:app --reload
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

cd ../frontend
npm test                # tests
npm run lint            # lint
npm run format          # formatage

cd ../e2e
npm run stack:up        # stack jetable pour les tests (http://localhost:8081)
npm test                # tests end-to-end
npm run test:ui         # les explorer dans l'interface Playwright
npm run test:headed     # les regarder en direct dans un navigateur, au ralenti
npm run test:debug      # les exécuter action par action
npm run stack:down      # supprime la stack de test et ses données

uvx pre-commit install  # hooks git (lint + détection de secrets)
```

## Documentation

- [Backend](docs/fr/BACK.md) : architecture, authentification, API, modèle de données, migrations, tests
- [Frontend](docs/fr/FRONT.md) : architecture, communication avec l'API, expérience utilisateur, tests
- [Conteneurs](docs/fr/CONTAINERS.md) : images, stack Docker Compose, durcissement, scans
- [Tests](docs/fr/TESTS.md) : stratégie de test, tests end-to-end, comment les regarder
- [Intégration continue](docs/fr/CI.md) : organisation du pipeline, règles, stages

## Licence

[MIT](LICENSE)
