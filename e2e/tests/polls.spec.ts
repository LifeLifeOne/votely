import { SAMPLE_POLLS, anotherUser, createPoll, expect, logIn, test } from './fixtures'

test.describe('polls', () => {
  test('a user creates a poll, votes and sees the results', async ({ page }) => {
    await logIn(page)
    const { question, options } = SAMPLE_POLLS[0]

    await page.goto('/')
    await page.getByRole('link', { name: 'New poll' }).click()
    await page.getByLabel('Question').fill(question)
    await page.getByRole('textbox', { name: 'Option 1' }).fill(options[0])
    await page.getByRole('textbox', { name: 'Option 2' }).fill(options[1])
    await page.getByRole('button', { name: 'Add an option' }).click()
    await page.getByRole('textbox', { name: 'Option 3' }).fill(options[2])
    await page.getByRole('button', { name: 'Create poll' }).click()

    await expect(page.getByRole('heading', { name: question })).toBeVisible()
    const pollPath = new URL(page.url()).pathname
    await page.getByRole('radio', { name: options[1] }).check()
    await page.getByRole('button', { name: 'Vote' }).click()

    await expect(page.getByText('Thanks, your vote has been recorded.')).toBeVisible()
    await expect(page.getByText('1 vote', { exact: true })).toBeVisible()
    await expect(page.getByRole('meter', { name: options[1] })).toHaveAttribute(
      'aria-valuenow',
      '100',
    )

    // The new poll is listed on the home page. It is found by its link, as other tests may
    // create polls with the same question.
    await page.getByRole('link', { name: 'Votely' }).click()
    await expect(page.locator(`a[href="${pollPath}"]`)).toContainText(question)
  })

  test('a user cannot vote twice on the same poll', async ({ page }) => {
    await logIn(page)
    const poll = await createPoll(page)
    await page.goto(`/polls/${poll.id}`)
    await page.getByRole('radio', { name: poll.options[0].label }).check()
    await page.getByRole('button', { name: 'Vote' }).click()
    await expect(page.getByText('Thanks, your vote has been recorded.')).toBeVisible()

    // The vote form does not come back after a reload...
    await page.reload()
    await expect(page.getByText('Thanks, your vote has been recorded.')).toBeVisible()
    await expect(page.getByRole('button', { name: 'Vote' })).toHaveCount(0)

    // ...and the API refuses a second vote sent directly.
    const second = await page.request.post(`/api/v1/polls/${poll.id}/votes`, {
      data: { option_id: poll.options[1].id },
    })
    expect(second.status()).toBe(409)
  })

  test('results update live when someone else votes', async ({ page, browser, baseURL }) => {
    await logIn(page)
    const poll = await createPoll(page)
    const choice = poll.options[1].label
    await page.goto(`/polls/${poll.id}`)
    await expect(page.getByText('0 votes', { exact: true })).toBeVisible()

    const other = await anotherUser(browser, baseURL!)
    await other.goto(`/polls/${poll.id}`)
    await other.getByRole('radio', { name: choice }).check()
    await other.getByRole('button', { name: 'Vote' }).click()
    await expect(other.getByText('Thanks, your vote has been recorded.')).toBeVisible()
    await other.context().close()

    // No reload: the page refreshes its results by itself (every 5 seconds).
    await expect(page.getByText('1 vote', { exact: true })).toBeVisible({ timeout: 10_000 })
    await expect(page.getByRole('meter', { name: choice })).toHaveAttribute('aria-valuenow', '100')
  })
})

test.describe('anonymous visitors', () => {
  test('can read polls and results but must log in to vote', async ({ page, browser, baseURL }) => {
    const author = await anotherUser(browser, baseURL!)
    const poll = await createPoll(author)
    await author.context().close()

    await page.goto(`/polls/${poll.id}`)

    await expect(page.getByRole('heading', { name: poll.question })).toBeVisible()
    await expect(page.getByText('0 votes', { exact: true })).toBeVisible()
    await expect(page.getByRole('main').getByRole('link', { name: 'Log in' })).toBeVisible()
    await expect(page.getByRole('radio')).toHaveCount(0)
  })

  test('are sent to the login page, then back to poll creation', async ({
    page,
    browser,
    baseURL,
  }) => {
    const setup = await browser.newContext({ baseURL })
    const email = await logIn(await setup.newPage())
    await setup.close()

    await page.goto('/')
    await page.getByRole('link', { name: 'New poll' }).click()
    await expect(page).toHaveURL(/\/login\?next=%2Fpolls%2Fnew$/)

    await page.getByLabel('Email').fill(email)
    await page.getByLabel('Password').fill('correct horse battery')
    await page.getByRole('button', { name: 'Log in' }).click()

    await expect(page.getByRole('heading', { name: 'New poll' })).toBeVisible()
  })
})
