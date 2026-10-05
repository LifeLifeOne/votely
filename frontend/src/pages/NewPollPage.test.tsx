import { screen } from '@testing-library/react'
import { http, HttpResponse } from 'msw'
import { beforeEach, expect, it } from 'vitest'

import { alice, poll } from '../test/fixtures'
import { renderApp } from '../test/renderApp'
import { server, session } from '../test/server'

beforeEach(() => {
  session.user = alice
})

it('sends anonymous visitors to the login page', async () => {
  session.user = null

  renderApp('/polls/new')

  expect(await screen.findByRole('heading', { name: 'Log in' })).toBeInTheDocument()
})

it('creates a poll and opens it', async () => {
  let sent: unknown
  server.use(
    http.post('/api/v1/polls', async ({ request }) => {
      sent = await request.json()
      return HttpResponse.json(poll, { status: 201 })
    }),
  )
  const { user } = renderApp('/polls/new')

  await user.type(await screen.findByLabelText('Question'), '  Where should we deploy?  ')
  await user.type(screen.getByLabelText('Option 1'), 'AWS')
  await user.type(screen.getByLabelText('Option 2'), 'GCP')
  await user.click(screen.getByRole('button', { name: 'Add an option' }))
  await user.type(screen.getByLabelText('Option 3'), 'Azure')
  await user.click(screen.getByRole('button', { name: 'Create poll' }))

  expect(await screen.findByRole('heading', { name: poll.question })).toBeInTheDocument()
  expect(sent).toEqual({ question: 'Where should we deploy?', options: ['AWS', 'GCP', 'Azure'] })
})

it('keeps at least two options', async () => {
  const { user } = renderApp('/polls/new')

  await user.click(await screen.findByRole('button', { name: 'Add an option' }))
  await user.click(screen.getByRole('button', { name: 'Remove option 3' }))

  expect(screen.getAllByRole('textbox', { name: /option/i })).toHaveLength(2)
  expect(screen.queryByRole('button', { name: /remove option/i })).not.toBeInTheDocument()
})

it('rejects duplicate options before calling the API', async () => {
  const { user } = renderApp('/polls/new')

  await user.type(await screen.findByLabelText('Question'), 'Tabs or spaces?')
  await user.type(screen.getByLabelText('Option 1'), 'Tabs')
  await user.type(screen.getByLabelText('Option 2'), 'tabs ')
  await user.click(screen.getByRole('button', { name: 'Create poll' }))

  expect(await screen.findByRole('alert')).toHaveTextContent('Options must be unique.')
})
