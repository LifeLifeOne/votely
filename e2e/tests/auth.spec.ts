import { PASSWORD, expect, logIn, test, uniqueEmail } from './fixtures'

test.describe('authentication', () => {
  test('a visitor signs up and is logged in', async ({ page, context }) => {
    await page.goto('/')
    await page.getByRole('link', { name: 'Sign up' }).click()
    await page.getByLabel('Email').fill(uniqueEmail('signup'))
    await page.getByLabel('Password').fill(PASSWORD)
    await page.getByRole('button', { name: 'Sign up' }).click()

    await expect(page.getByRole('button', { name: 'Log out' })).toBeVisible()
    // The session is a cookie JavaScript cannot read.
    const session = (await context.cookies()).find((cookie) => cookie.name === 'votely_session')
    expect(session?.httpOnly).toBe(true)
    expect(session?.sameSite).toBe('Lax')
  })

  test('a user logs in with the login form', async ({ page, browser, baseURL }) => {
    // Create the account in another context, then log in through the UI.
    const setup = await browser.newContext({ baseURL })
    const email = await logIn(await setup.newPage())
    await setup.close()

    await page.goto('/login')
    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill(PASSWORD)
    await page.getByRole('button', { name: 'Log in' }).click()

    await expect(page.getByRole('button', { name: 'Log out' })).toBeVisible()
  })

  test('wrong credentials are rejected', async ({ page }) => {
    await page.goto('/login')
    await page.getByLabel('Email').fill(uniqueEmail('nobody'))
    await page.getByLabel('Password').fill('wrong password!!')
    await page.getByRole('button', { name: 'Log in' }).click()

    await expect(page.getByRole('alert')).toHaveText('Invalid email or password')
  })

  test('a user logs out', async ({ page }) => {
    await logIn(page)
    await page.goto('/')

    await page.getByRole('button', { name: 'Log out' }).click()

    await expect(page.getByRole('link', { name: 'Log in' })).toBeVisible()
    expect((await page.request.get('/api/v1/auth/me')).status()).toBe(401)
  })
})
