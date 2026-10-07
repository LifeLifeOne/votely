# Votely

[![English](https://img.shields.io/badge/lang-English-blue)](README.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](README.fr.md) [![pipeline](https://gitlab.com/StateOfFlowHunter/votely/badges/main/pipeline.svg)](https://gitlab.com/StateOfFlowHunter/votely/-/pipelines) [![coverage](https://gitlab.com/StateOfFlowHunter/votely/badges/main/coverage.svg)](https://gitlab.com/StateOfFlowHunter/votely/-/pipelines) [![version](https://img.shields.io/gitlab/v/tag/StateOfFlowHunter%2Fvotely?label=version)](https://gitlab.com/StateOfFlowHunter/votely/-/tags)

> [!TIP]
> 🛠️ **This is a DevOps showcase project**: the app is deliberately simple, the focus is on how it
> is built, tested, secured, shipped and run.

![GitLab CI](https://img.shields.io/badge/GitLab_CI-FC6D26?logo=gitlab&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes&logoColor=white)
![Helm](https://img.shields.io/badge/Helm-0F1689?logo=helm&logoColor=white)
![Playwright](https://img.shields.io/badge/Playwright-2EAD33?logo=playwright&logoColor=white)
![Trivy](https://img.shields.io/badge/Trivy-1904DA?logo=aqua&logoColor=white)

Votely is a lightweight polling application: create a poll, share it, collect votes (one per account) and follow the results live.

## Stack

| Layer | Technology |
|---|---|
| Frontend | React 19 · TypeScript · Vite · TanStack Query |
| Backend | Python 3.12 · FastAPI · SQLAlchemy 2 · Alembic |
| Database | PostgreSQL 16 |
| Containers | Docker multi-stage images · nginx · Docker Compose |
| Tests | pytest · Vitest · Testing Library · MSW · Playwright |
| CI/CD | GitLab CI · gitleaks · Semgrep · Trivy · crane |
| Kubernetes | Helm charts · Traefik ingress · kind (local cluster) |

## Repository layout

```
.
├── backend/          # REST API (FastAPI)
├── e2e/              # End-to-end tests (Playwright)
├── frontend/         # Web application (React)
├── compose.yaml      # Full stack (Docker Compose)
├── compose.e2e.yaml  # Disposable stack for end-to-end tests
├── deploy/           # Kubernetes: Helm charts, local cluster (kind)
└── docs/             # Technical documentation (en/, fr/)
```

## Getting started

### Run the full stack with Docker

```bash
cp .env.example .env          # then set a database password and a JWT secret (openssl rand -hex 32)
docker compose up --build     # http://localhost:8080
```

### Run on Kubernetes (local cluster)

Prerequisites: Docker, [mise](https://mise.jdx.dev/).

```bash
mise install                  # kind, kubectl and Helm versions pinned in .mise.toml
deploy/kind/up.sh             # http://votely.localhost (images published by the CI)
deploy/kind/down.sh           # delete the cluster
```

### Local development

Prerequisites: Docker, [mise](https://mise.jdx.dev/) (installs Python 3.12, uv, Node.js 24 and the Kubernetes tools).

```bash
mise install                  # tool versions pinned in .mise.toml
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

cd ../frontend
npm test                # tests
npm run lint            # lint
npm run format          # format

cd ../e2e
npm run stack:up        # disposable stack for the tests (http://localhost:8081)
npm test                # end-to-end tests
npm run test:ui         # explore them in the Playwright UI
npm run test:headed     # watch them live in a browser, slowed down
npm run test:debug      # step through them action by action
npm run stack:down      # remove the test stack and its data

uvx pre-commit install  # git hooks (lint + secret scanning)
```

## Documentation

- [Backend](docs/en/BACK.md): architecture, authentication, API, data model, migrations, tests
- [Frontend](docs/en/FRONT.md): architecture, API communication, user experience, tests
- [Containers](docs/en/CONTAINERS.md): images, Docker Compose stack, hardening, scans
- [Tests](docs/en/TESTS.md): testing strategy, end-to-end tests, how to watch them
- [Continuous integration](docs/en/CI.md): pipeline layout, rules, stages, releases
- [Kubernetes](docs/en/KUBERNETES.md): Helm charts, local cluster, AWS server with HTTPS, migrations, security settings
- [GitOps](docs/en/GITOPS.md): Argo CD, staging and production, deploying, rolling back, sealed secrets
- [Infrastructure](docs/en/INFRA.md): AWS access, Terraform state, network and server, CI access, signing key, costs

## License

[MIT](LICENSE)
