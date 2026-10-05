import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import { poll, results } from './fixtures'

// Default API responses: an anonymous visitor and a single poll.
// Tests override them with server.use(...) when they need another scenario.
export const handlers = [
  http.get('/api/v1/auth/me', () =>
    HttpResponse.json({ detail: 'not authenticated' }, { status: 401 }),
  ),
  http.get('/api/v1/polls', () => HttpResponse.json([poll])),
  http.get('/api/v1/polls/:id', ({ params }) =>
    params.id === poll.id
      ? HttpResponse.json(poll)
      : HttpResponse.json({ detail: 'poll not found' }, { status: 404 }),
  ),
  http.get('/api/v1/polls/:id/results', () => HttpResponse.json(results)),
]

export const server = setupServer(...handlers)
