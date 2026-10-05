# Continuous integration

[![English](https://img.shields.io/badge/lang-English-blue)](CI.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](../fr/CI.md)

Votely is built and tested by GitLab CI on every merge request and on every commit to `main`.
Pipelines: https://gitlab.com/StateOfFlowHunter/votely/-/pipelines

## Layout

```
.gitlab-ci.yml                  # entry point: workflow, stages, defaults, includes
.gitlab/ci/
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

## Caching

Dependencies are cached per component, keyed on the lockfile (`uv.lock`, `package-lock.json`):
the cache is reused until dependencies change. Lockfiles are always respected (`UV_FROZEN`,
`npm ci`), so CI never installs something different from what was reviewed.

## Images

| Component | CI image |
|---|---|
| Backend | `ghcr.io/astral-sh/uv:0.12-python3.12-trixie-slim` (same Python and Debian as the production image) |
| Frontend, e2e | `node:24-alpine` |
