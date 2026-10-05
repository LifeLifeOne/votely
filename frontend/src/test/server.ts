import { http, HttpResponse } from 'msw'
import { setupServer } from 'msw/node'

import type { Credentials } from '../api/auth'
import type { NewPoll } from '../api/polls'
import type { User } from '../api/types'
import { PASSWORD, alice, poll, results } from './fixtures'

/** Fake server-side state, reset after each test. Set `session.user` to start logged in. */
export const session: {
  user: User | null
  accounts: Map<string, string>
  votedPollIds: Set<string>
} = { user: null, accounts: new Map(), votedPollIds: new Set() }

export function resetSession() {
  session.user = null
  session.accounts = new Map([[alice.email, PASSWORD]])
  session.votedPollIds = new Set()
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
  http.post('/api/v1/polls', async ({ request }) => {
    if (!session.user) return unauthorized()
    const { question } = (await request.json()) as NewPoll
    return HttpResponse.json({ ...poll, question }, { status: 201 })
  }),
  http.get('/api/v1/polls/:id', ({ params }) =>
    params.id === poll.id
      ? HttpResponse.json({ ...poll, has_voted: session.votedPollIds.has(poll.id) })
      : HttpResponse.json({ detail: 'poll not found' }, { status: 404 }),
  ),
  http.post('/api/v1/polls/:id/votes', ({ params }) => {
    if (!session.user) return unauthorized()
    if (session.votedPollIds.has(String(params.id))) {
      return HttpResponse.json({ detail: 'already voted on this poll' }, { status: 409 })
    }
    session.votedPollIds.add(String(params.id))
    return new HttpResponse(null, { status: 204 })
  }),
  http.get('/api/v1/polls/:id/results', () => HttpResponse.json(results)),
]

export const server = setupServer(...handlers)
