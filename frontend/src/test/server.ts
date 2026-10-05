import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import type { Credentials } from '../api/auth'
import type { User } from '../api/types'
import { PASSWORD, alice, poll, results } from './fixtures'

/** Fake server-side state, reset after each test. Set `session.user` to start logged in. */
export const session: { user: User | null; accounts: Map<string, string> } = {
  user: null,
  accounts: new Map(),
}

export function resetSession() {
  session.user = null
  session.accounts = new Map([[alice.email, PASSWORD]])
}
resetSession()

const unauthorized = () => HttpResponse.json({ detail: 'not authenticated' }, { status: 401 })

// Default API behaviour: alice has an account, a single poll exists.
// Tests override handlers with server.use(...) when they need another scenario.
export const handlers = [
  http.get('/api/v1/auth/me', () =>
    session.user ? HttpResponse.json(session.user) : unauthorized(),
  ),
  http.post('/api/v1/auth/login', async ({ request }) => {
    const { email, password } = (await request.json()) as Credentials
    if (session.accounts.get(email) !== password) {
      return HttpResponse.json({ detail: 'invalid email or password' }, { status: 401 })
    }
    session.user = { ...alice, email }
    return new HttpResponse(null, { status: 204 })
  }),
  http.post('/api/v1/auth/register', async ({ request }) => {
    const { email, password } = (await request.json()) as Credentials
    if (session.accounts.has(email)) {
      return HttpResponse.json({ detail: 'email already registered' }, { status: 409 })
    }
    session.accounts.set(email, password)
    return HttpResponse.json({ ...alice, email }, { status: 201 })
  }),
  http.post('/api/v1/auth/logout', () => {
    session.user = null
    return new HttpResponse(null, { status: 204 })
  }),
  http.get('/api/v1/polls', () => HttpResponse.json([poll])),
  http.get('/api/v1/polls/:id', ({ params }) =>
    params.id === poll.id
      ? HttpResponse.json(poll)
      : HttpResponse.json({ detail: 'poll not found' }, { status: 404 }),
  ),
  http.get('/api/v1/polls/:id/results', () => HttpResponse.json(results)),
]

export const server = setupServer(...handlers)
