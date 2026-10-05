# Frontend

[![English](https://img.shields.io/badge/lang-English-blue)](FRONT.md) [![Français](https://img.shields.io/badge/lang-Fran%C3%A7ais-lightgrey)](../fr/FRONT.md)

Single-page application written in React 19 and TypeScript (strict mode), built with Vite.

| Concern | Choice | Why |
|---|---|---|
| Routing | React Router | De facto standard, URL-driven pages |
| Server state | TanStack Query | Caching, refetching and invalidation without hand-written state |
| Styling | Plain CSS with variables | Small app, no framework needed; one light theme |
| Lint / format | oxlint, Prettier | Fast linting, consistent formatting |
| Tests | Vitest, Testing Library, MSW | Tests use the app like a user, against a fake HTTP API |

## Architecture

```
frontend/src/
├── api/          # HTTP client, one function per endpoint, response types
├── auth/         # Session hooks (current user, login, logout), safe redirects
├── components/   # Layout, vote form, results chart, auth guard, status messages
├── pages/        # One component per route
├── test/         # Test setup, fake API (MSW), fixtures, render helper
└── AppRoutes.tsx # Route table
```

Components never call `fetch` directly: they use TanStack Query hooks, which call the
functions of `src/api/`. All server data lives in the query cache; there is no global store.

| Route | Page | Access |
|---|---|---|
| `/` | Poll list | public |
| `/polls/:id` | Poll, vote form and live results | public, voting requires login |
| `/polls/new` | Poll creation | logged in (otherwise redirected to login) |
| `/login`, `/register` | Authentication | public |

## Talking to the API

The browser only talks to **one origin**. Requests go to relative paths (`/api/v1/...`) and
are routed to the backend by:

| Environment | Router |
|---|---|
| Development (`npm run dev`) | Vite dev server proxy (`vite.config.ts`) |
| Docker Compose | nginx serving the frontend |
| Kubernetes | Ingress (`/api` → backend, `/` → frontend) |

Consequences:

- **No CORS** configuration is needed anywhere.
- The **session cookie** (`HttpOnly`, `SameSite=Lax`) is sent automatically. The frontend never
  sees or stores a token: there is nothing for an XSS attack to steal.
- The **same build** runs in every environment: the API URL is not baked into the bundle, so
  one image is promoted from staging to production.

The API client (`src/api/client.ts`) turns error responses into an `ApiError` carrying the HTTP
status and the API message, which pages display as is.

## User experience

- `has_voted`, returned by the API, replaces the vote form with a confirmation; a second vote is
  impossible from the UI and refused by the API anyway (`409`).
- Results are refreshed every 5 seconds while a poll is open on screen.
- After login, the user is sent back to the page they came from (`?next=`). Only local paths
  are accepted, to avoid open redirects.
- Validation mirrors the API rules (2–10 unique options, password ≥ 12 characters) for
  immediate feedback; the API remains the source of truth.
- Accessible markup: labelled fields, `role="alert"` for errors, `role="meter"` for result bars,
  visible focus, reduced motion respected.

## Development

```bash
cd frontend
npm ci
npm run dev            # http://localhost:5173, proxies /api to http://localhost:8000
```

The backend must be running (see [BACK.md](BACK.md)). Another API address can be used with
`VOTELY_API_URL=http://host:port npm run dev`.

| Command | Purpose |
|---|---|
| `npm run build` | Type-check and build to `dist/` |
| `npm run typecheck` | TypeScript only |
| `npm run lint` | oxlint (warnings fail the command) |
| `npm run format` / `format:check` | Prettier |
| `npm test` / `test:watch` | Vitest |
| `npm run test:coverage` | Tests with coverage (minimum 80 % of lines) |

## Tests

Tests render the whole application at a given URL (`renderApp('/polls/42')`) and interact with
it as a user would: by roles and labels, typing and clicking.

The API is replaced by [MSW](https://mswjs.io/) (`src/test/server.ts`), which intercepts real
`fetch` calls. The fake API keeps a small state (accounts, session, votes), so flows such as
"sign up then see my email in the header" or "vote then see the confirmation" are tested end
to end inside the frontend. Any request without a handler fails the test.

What is covered:

- API client: success, `204`, error messages, validation errors, non-JSON errors.
- Pages: poll list (empty state, badges, errors), poll detail (results, 404), creation (guard,
  dynamic options, duplicates), login / registration / logout, safe redirects.
- Vote form: anonymous visitor, successful vote, already voted, closed poll, refused vote.

Browser-level tests against the real backend come with the end-to-end suite (see TESTS.md).

## Known limitations

- Anonymous visitors trigger a `401` on `GET /api/v1/auth/me`, which browsers log in the
  console. It is the expected answer ("not logged in") and is handled by the app.
- Results use polling, not WebSockets: simple and good enough for this traffic.
