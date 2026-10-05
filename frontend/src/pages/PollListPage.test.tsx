import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { expect, it } from 'vitest'

import { poll } from '../test/fixtures'
import { renderApp } from '../test/renderApp'
import { server } from '../test/server'

it('lists polls with a link to each of them', async () => {
  renderApp('/')

  const link = await screen.findByRole('link', { name: /where should we deploy/i })
  expect(link).toHaveAttribute('href', `/polls/${poll.id}`)
})

it('shows closed and already voted polls', async () => {
  server.use(
    http.get('/api/v1/polls', () =>
      HttpResponse.json([{ ...poll, is_closed: true, has_voted: true }]),
    ),
  )

  renderApp('/')

  expect(await screen.findByText('Closed')).toBeInTheDocument()
  expect(screen.getByText('Voted')).toBeInTheDocument()
})

it('shows an empty state', async () => {
  server.use(http.get('/api/v1/polls', () => HttpResponse.json([])))

  renderApp('/')

  expect(await screen.findByText('No polls yet.')).toBeInTheDocument()
})

it('shows API errors', async () => {
  server.use(
    http.get('/api/v1/polls', () =>
      HttpResponse.json({ detail: 'database unavailable' }, { status: 503 }),
    ),
  )

  renderApp('/')

  expect(await screen.findByRole('alert')).toHaveTextContent('Database unavailable')
})
