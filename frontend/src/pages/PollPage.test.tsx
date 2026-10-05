import { screen } from '@testing-library/react'
import { expect, it } from 'vitest'

import { poll } from '../test/fixtures'
import { renderApp } from '../test/renderApp'

it('shows the question and the results', async () => {
  renderApp(`/polls/${poll.id}`)

  expect(await screen.findByRole('heading', { name: poll.question })).toBeInTheDocument()
  expect(await screen.findByText('4 votes')).toBeInTheDocument()
  expect(screen.getByRole('meter', { name: 'AWS' })).toHaveAttribute('aria-valuenow', '75')
  expect(screen.getByRole('meter', { name: 'GCP' })).toHaveAttribute('aria-valuenow', '25')
})

it('shows a not found message for unknown polls', async () => {
  renderApp('/polls/unknown')

  expect(await screen.findByRole('heading', { name: 'Poll not found' })).toBeInTheDocument()
})

it('shows a not found page for unknown routes', async () => {
  renderApp('/nowhere')

  expect(await screen.findByRole('heading', { name: 'Page not found' })).toBeInTheDocument()
})
