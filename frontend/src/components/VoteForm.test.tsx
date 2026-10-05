import { screen, within } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { expect, it } from 'vitest'

import { alice, poll } from '../test/fixtures'
import { renderApp } from '../test/renderApp'
import { server, session } from '../test/server'

const pollUrl = `/polls/${poll.id}`

it('asks anonymous visitors to log in', async () => {
  renderApp(pollUrl)

  await screen.findByRole('heading', { name: poll.question })
  const main = within(screen.getByRole('main'))
  expect(main.getByRole('link', { name: 'Log in' }).closest('p')).toHaveTextContent(
    'Log in to vote.',
  )
  expect(screen.queryByRole('radio')).not.toBeInTheDocument()
})

it('lets a logged-in user vote once', async () => {
  session.user = alice
  const { user } = renderApp(pollUrl)

  const vote = await screen.findByRole('button', { name: 'Vote' })
  expect(vote).toBeDisabled()
  await user.click(screen.getByRole('radio', { name: 'AWS' }))
  await user.click(vote)

  expect(await screen.findByText('Thanks, your vote has been recorded.')).toBeInTheDocument()
  expect(screen.queryByRole('radio')).not.toBeInTheDocument()
})

it('does not offer to vote twice', async () => {
  session.user = alice
  session.votedPollIds.add(poll.id)

  renderApp(pollUrl)

  expect(await screen.findByText('Thanks, your vote has been recorded.')).toBeInTheDocument()
})

it('does not offer to vote on a closed poll', async () => {
  session.user = alice
  server.use(http.get('/api/v1/polls/:id', () => HttpResponse.json({ ...poll, is_closed: true })))

  renderApp(pollUrl)

  expect(await screen.findByText('This poll is closed.')).toBeInTheDocument()
})

it('shows the API error when the vote is refused', async () => {
  session.user = alice
  server.use(
    http.post('/api/v1/polls/:id/votes', () =>
      HttpResponse.json({ detail: 'poll is closed' }, { status: 409 }),
    ),
  )
  const { user } = renderApp(pollUrl)

  await user.click(await screen.findByRole('radio', { name: 'GCP' }))
  await user.click(screen.getByRole('button', { name: 'Vote' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('Poll is closed')
})
