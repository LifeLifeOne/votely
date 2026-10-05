# Backend

REST API written in Python 3.12 with FastAPI, SQLAlchemy 2 and PostgreSQL 16.
Dependencies are managed with [uv](https://docs.astral.sh/uv/) (`pyproject.toml` + `uv.lock`).

## Architecture

The code is split into three layers. Dependencies only point inwards: the API knows the
domain, the domain only knows the repository contracts.

```
backend/app/
├── api/            # HTTP layer: routes, schemas, auth dependencies, error mapping
├── domain/         # Business rules (PollService, UserService) and domain errors
├── repositories/   # Persistence: SQLAlchemy models and SQL repositories
└── core/           # Cross-cutting concerns: settings, database session, security, logging
```

| Layer | Responsibility | Example |
|---|---|---|
| `api` | Validate input shape, authenticate, call the service, serialize output | `PollCreate` requires 2–10 unique options |
| `domain` | Rules that depend on time or stored data | voting on a closed poll is rejected |
| `repositories` | SQL queries, transactions, constraint violations | a duplicate vote becomes `AlreadyVotedError` |

Services depend on repository **protocols** (`PollRepository`, `UserRepository`), not on
SQLAlchemy directly. Unit tests inject in-memory fakes (`tests/unit/fakes.py`) and a fixed
clock, so business rules are tested in milliseconds without a database.

Domain errors are plain Python exceptions (`app/domain/errors.py`), translated to HTTP status
codes in a single place (`app/api/errors.py`).

## Authentication

Accounts are local (email + password). After login, the session is a signed JWT stored in a
cookie; the browser sends it automatically, the frontend never handles the token.

| Measure | Why |
|---|---|
| Passwords hashed with **Argon2id** (`pwdlib`) | Memory-hard algorithm, resistant to GPU cracking |
| Password length 12–128 characters | Length matters more than complexity rules |
| Emails stored lowercased, unique constraint | `Alice@x.com` and `alice@x.com` are the same account |
| Same error and same timing for unknown email and wrong password | Login cannot be used to discover accounts |
| JWT **HS256**, signed with `VOTELY_JWT_SECRET` (≥ 32 chars, required) | The app refuses to start with a missing or weak key |
| Short-lived token (`exp`, 60 min by default) | Limits the impact of a leaked token |
| Cookie `HttpOnly` | Not readable by JavaScript, so not stealable through XSS |
| Cookie `SameSite=Lax` | Not sent on cross-site POST requests, which blocks CSRF |
| Cookie `Secure` (default) | Only sent over HTTPS; disabled explicitly for local HTTP |

Permissions:

| Action | Anonymous | Logged in |
|---|---|---|
| List / read polls and results | ✅ | ✅ |
| Create a poll (the user becomes its author) | ❌ `401` | ✅ |
| Vote | ❌ `401` | ✅ once per poll |

### One vote per user and poll

The rule is enforced by a **unique constraint** `(poll_id, user_id)` on `votes`, not only by a
check in Python: two concurrent requests could both pass a "has this user voted?" check, but
only one insert can satisfy the constraint. The repository translates that specific constraint
violation into `AlreadyVotedError` (`409`). Votes are final.

`has_voted` is returned with each poll so the frontend can disable the vote button; it is
computed with a single query for a whole page of polls.

## API

All business endpoints are versioned under `/api/v1`. Interactive documentation is generated
by FastAPI at `/docs` (Swagger UI) and `/redoc`.

| Method | Path | Auth | Description | Success |
|---|---|---|---|---|
| `POST` | `/api/v1/auth/register` | – | Create an account | `201` |
| `POST` | `/api/v1/auth/login` | – | Open a session (sets the cookie) | `204` |
| `POST` | `/api/v1/auth/logout` | – | Close the session (clears the cookie) | `204` |
| `GET` | `/api/v1/auth/me` | required | Current user | `200` |
| `POST` | `/api/v1/polls` | required | Create a poll | `201` |
| `GET` | `/api/v1/polls?limit=20&offset=0` | optional | List polls, newest first | `200` |
| `GET` | `/api/v1/polls/{id}` | optional | Get a poll and its options | `200` |
| `POST` | `/api/v1/polls/{id}/votes` | required | Vote for an option | `204` |
| `GET` | `/api/v1/polls/{id}/results` | – | Vote counts and percentages | `200` |
| `GET` | `/healthz` | – | Liveness probe (never touches the database) | `200` |
| `GET` | `/readyz` | – | Readiness probe (`SELECT 1`) | `200` / `503` |

Example session with curl:

```bash
curl -X POST localhost:8000/api/v1/auth/register -H 'content-type: application/json' \
  -d '{"email": "alice@example.com", "password": "correct horse battery"}'
curl -c cookies.txt -X POST localhost:8000/api/v1/auth/login -H 'content-type: application/json' \
  -d '{"email": "alice@example.com", "password": "correct horse battery"}'
curl -b cookies.txt -X POST localhost:8000/api/v1/polls -H 'content-type: application/json' \
  -d '{"question": "Where should we deploy?", "options": ["AWS", "GCP", "Azure"]}'
```

### Errors

| Status | When |
|---|---|
| `401` | Not logged in, invalid or expired session, wrong credentials |
| `404` | Unknown poll |
| `409` | Email already registered, poll closed, user already voted |
| `422` | Invalid payload, option not part of the poll, closing date in the past |

Error bodies always have the shape `{"detail": ...}`.

## Data model

```mermaid
erDiagram
    users ||--o{ polls : authors
    users ||--o{ votes : casts
    polls ||--|{ options : has
    polls ||--o{ votes : receives
    options ||--o{ votes : counts
```

| Table | Notes |
|---|---|
| `users` | UUID primary key, unique lowercased `email`, Argon2 `password_hash` |
| `polls` | UUID primary key, `author_id` (set to `NULL` if the user is deleted), optional `closes_at`, indexed `created_at` |
| `options` | Ordered by `position`, unique per poll, deleted with their poll |
| `votes` | `BIGINT` identity, `poll_id` + `option_id` + `user_id`, unique `(poll_id, user_id)` |

UUIDs are used for public identifiers so ids cannot be enumerated.
Constraint names follow a naming convention (`app/repositories/models.py`) so migrations stay
deterministic, and so the code can recognize a specific constraint violation.

`polls.author_id` and `votes.user_id` are nullable on purpose: data created before accounts
existed is kept rather than deleted by a migration.

## Configuration

Settings are read from environment variables prefixed with `VOTELY_` (12-factor), with an
optional `.env` file for local development. Invalid settings stop the application at startup.

| Variable | Default | Description |
|---|---|---|
| `VOTELY_DATABASE_URL` | `postgresql+psycopg://votely:votely@localhost:5432/votely` | SQLAlchemy URL |
| `VOTELY_JWT_SECRET` | – (**required**, ≥ 32 chars) | Session signing key, e.g. `openssl rand -hex 32` |
| `VOTELY_ACCESS_TOKEN_TTL_MINUTES` | `60` | Session lifetime |
| `VOTELY_COOKIE_SECURE` | `true` | Set to `false` only for local development over HTTP |
| `VOTELY_LOG_LEVEL` | `INFO` | Python log level |

## Database migrations

Schema changes are managed with Alembic (`backend/alembic/`).

```bash
uv run alembic upgrade head                                  # apply migrations
uv run alembic revision --autogenerate -m "add poll author"  # create a migration
uv run alembic downgrade -1                                  # roll back one step
```

Autogenerated migrations must always be reviewed: Alembic does not know about existing data.
For example, `one vote per user and poll` adds `votes.poll_id` as nullable, backfills it from
`options`, and only then makes it `NOT NULL`; the generated version would have failed on any
database containing votes.

## Tests

```bash
docker compose up -d db   # integration tests need PostgreSQL
uv run pytest             # unit + integration, with coverage (minimum 90 %)
uv run pytest tests/unit  # fast, no database
```

- **Unit tests** (`tests/unit`): domain rules, schema validation, settings, password hashing and
  tokens, no I/O.
- **Integration tests** (`tests/integration`): HTTP calls against a real PostgreSQL, with
  anonymous and logged-in clients (`login_as` fixture). They use a dedicated `<db>_test`
  database, created automatically and migrated with Alembic, so migrations are tested on every
  run; tables are truncated between tests.
- **Migration test**: downgrades the schema, inserts legacy data, upgrades again and checks the
  data survived.

Without PostgreSQL, integration tests are skipped locally; in CI (`CI` variable set) they fail
instead, so a broken database setup can never go unnoticed.

## Known limitations

- No rate limiting on login and registration yet (brute force protection).
- No email verification or password reset.
- Sessions cannot be revoked server-side before they expire: logout removes the cookie from
  the browser, which is why tokens are short-lived.
