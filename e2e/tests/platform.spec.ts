import { expect, test } from './fixtures'

// Properties of the deployed stack rather than features: probes and HTTP hardening.
test.describe('platform', () => {
  test('health endpoints answer', async ({ request }) => {
    expect((await request.get('/healthz')).status()).toBe(200)
    expect(await (await request.get('/api/v1/polls')).json()).toBeInstanceOf(Array)
  })

  test('pages are served with security headers', async ({ request }) => {
    const response = await request.get('/')
    const headers = response.headers()

    expect(headers['content-security-policy']).toContain("default-src 'self'")
    expect(headers['content-security-policy']).toContain("frame-ancestors 'none'")
    expect(headers['x-content-type-options']).toBe('nosniff')
    expect(headers['server']).toBe('nginx') // no version disclosed
  })

  test('client-side routes work on direct access', async ({ page }) => {
    const response = await page.goto('/polls/new')

    expect(response?.status()).toBe(200)
    await expect(page.getByRole('heading', { name: 'Log in' })).toBeVisible()
  })

  test('the page has no console errors besides the anonymous session check', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (message) => {
      if (message.type() === 'error' && !message.text().includes('401')) errors.push(message.text())
    })
    page.on('pageerror', (error) => errors.push(error.message))

    await page.goto('/')
    await expect(page.getByRole('heading', { name: 'Polls' })).toBeVisible()

    expect(errors).toEqual([])
  })
})
