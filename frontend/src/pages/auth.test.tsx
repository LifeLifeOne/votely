import { screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'

import { safeRedirect } from '../auth/redirect'
import { PASSWORD, alice } from '../test/fixtures'
import { renderApp } from '../test/renderApp'
import { session } from '../test/server'

describe('login', () => {
  it('logs the user in and shows their email', async () => {
    const { user } = renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), alice.email)
    await user.type(screen.getByLabelText('Password'), PASSWORD)
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByText(alice.email)).toBeInTheDocument()
    expect(await screen.findByRole('heading', { name: 'Polls' })).toBeInTheDocument()
  })

  it('shows an error with wrong credentials', async () => {
    const { user } = renderApp('/login')

    await user.type(await screen.findByLabelText('Email'), alice.email)
    await user.type(screen.getByLabelText('Password'), 'wrong password!!')
    await user.click(screen.getByRole('button', { name: 'Log in' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Invalid email or password')
  })

  it.each([
    ['/polls/42', '/polls/42'],
    [null, '/'],
    ['https://evil.example', '/'],
    ['//evil.example', '/'],
  ])('only redirects to local paths (%s)', (next, expected) => {
    expect(safeRedirect(next)).toBe(expected)
  })
})

describe('registration', () => {
  it('creates the account and logs the user in', async () => {
    const { user } = renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), 'bob@example.com')
    await user.type(screen.getByLabelText('Password'), PASSWORD)
    await user.click(screen.getByRole('button', { name: 'Sign up' }))

    expect(await screen.findByText('bob@example.com')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Log out' })).toBeInTheDocument()
  })

  it('shows an error when the email is already used', async () => {
    const { user } = renderApp('/register')

    await user.type(await screen.findByLabelText('Email'), alice.email)
    await user.type(screen.getByLabelText('Password'), PASSWORD)
    await user.click(screen.getByRole('button', { name: 'Sign up' }))

    expect(await screen.findByRole('alert')).toHaveTextContent('Email already registered')
  })
})

describe('logout', () => {
  it('ends the session', async () => {
    session.user = alice
    const { user } = renderApp('/')

    await user.click(await screen.findByRole('button', { name: 'Log out' }))

    expect(await screen.findByRole('link', { name: 'Log in' })).toBeInTheDocument()
    expect(screen.queryByText(alice.email)).not.toBeInTheDocument()
  })
})
