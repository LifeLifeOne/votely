# Continuous integration

[![English](https://img.shields.io/badge/lang-English-blue)](CI.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](../fr/CI.md)

Votely is built and tested by GitLab CI on every merge request and on every commit to `main`.
Pipelines: https://gitlab.com/StateOfFlowHunter/votely/-/pipelines

## Layout

```
.gitlab-ci.yml                  # entry point: workflow, stages, defaults, includes
.gitlab/ci/
├── templates.gitlab-ci.yml     # shared building blocks (Docker build, rules)
├── backend.gitlab-ci.yml       # backend:* jobs
├── frontend.gitlab-ci.yml      # frontend:* jobs
└── e2e.gitlab-ci.yml           # e2e:* jobs
```

- One file per component: everything that concerns the backend pipeline is in one place, while
  the stages are declared once in `.gitlab-ci.yml`.
- The `.gitlab-ci.yml` suffix lets editors and the GitLab tooling recognise and validate the files.
- Jobs are named `<component>:<action>` (`backend:lint`, `frontend:lint`), so the pipeline graph
  reads at a glance.
- Each file starts with a hidden job (`.backend`, `.frontend`, `.e2e`) holding the image, cache
  and rules shared by the component's jobs, which `extends` it.

## When pipelines run

| Event | Pipeline | Jobs |
|---|---|---|
| Merge request | yes | only components whose files (or their CI file) changed |
| Push to a branch with an open merge request | no (the merge request pipeline covers it) | – |
| Push to `main` | yes | all jobs |
| Tag | yes | all jobs |

Filtering merge request jobs by changed paths keeps pipelines fast and saves CI minutes; `main`
always runs everything, so the default branch is always fully verified.

A new push cancels the running pipeline of the same branch (`interruptible` jobs). Jobs are
retried once on infrastructure failures only, never on a failing test or lint.

## Stages

| Stage | Job | What it checks |
|---|---|---|
| `lint` | `backend:lint` | ruff (lint rules, import order) and ruff format |
| | `frontend:lint` | oxlint (warnings fail the job), Prettier, TypeScript |
| | `e2e:lint` | Prettier, TypeScript |
| `test` | `backend:test` | pytest: unit and integration tests against a PostgreSQL 16 service, migrations included; coverage ≥ 90 % |
| | `frontend:test` | Vitest: components and pages against a fake API (MSW); coverage ≥ 80 % of lines |
| `build` | `backend:build`, `frontend:build` | Production images built and pushed to the GitLab container registry |

Each test job only waits for the lint job of its own component (`needs`), so a slow frontend lint
never delays the backend tests.

`backend:test` sets `CI=true` (always defined by GitLab): if PostgreSQL were unreachable, the
integration tests would fail instead of being skipped as they are locally.

## Container images

Images are pushed to the project's container registry:
`registry.gitlab.com/stateofflowhunter/votely/<component>:<commit SHA>`.

- **Immutable tags**: the full commit SHA identifies exactly what was built. Deployment tags
  (`main`, versions) are added later, after the images have been tested.
- **Never untested**: each build job `needs` the tests of its component, so a failing test stops
  the image from being published.
- **Both images, or none**: build jobs run when any application path changes (`.rules:app`), so
  the end-to-end tests always run a backend and a frontend from the same commit. Rebuilding an
  unchanged image is fast thanks to the layer cache.
- **Layer cache in the registry** (`:buildcache`, BuildKit `mode=max`): written by the default
  branch only, read by every pipeline.
- **Traceability**: OCI labels record the source repository, the commit and the build date.
- **Digest handed to later jobs**: each build exports `BACKEND_IMAGE` / `FRONTEND_IMAGE`
  (`…@sha256:…`) as a dotenv artifact, so later jobs use exactly the image that was built, not a
  tag that could move.

Builds use Docker-in-Docker with BuildKit (`docker buildx`), the standard setup on GitLab.com
shared runners.

## Reports

| Report | Where it shows up |
|---|---|
| JUnit (`junit.xml`) | *Tests* tab of the pipeline, and the merge request widget (new and fixed failures) |
| Coverage percentage | Merge request widget and job list, extracted from the job log |
| Cobertura (`coverage.xml`) | Covered and uncovered lines highlighted in the merge request diff |

Reports are uploaded even when tests fail (`when: always`) and kept one week.

## Caching

Dependencies are cached per component, keyed on the lockfile (`uv.lock`, `package-lock.json`):
the cache is reused until dependencies change. Lockfiles are always respected (`UV_FROZEN`,
`npm ci`), so CI never installs something different from what was reviewed.

## Images

| Component | CI image |
|---|---|
| Backend | `ghcr.io/astral-sh/uv:0.12-python3.12-trixie-slim` (same Python and Debian as the production image) |
| Frontend, e2e | `node:24-alpine` |
