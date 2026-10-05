import { test as base, expect, type Browser, type Page } from '@playwright/test'

export const PASSWORD = 'correct horse battery'

/** A unique email per call, so tests never depend on each other or on existing data. */
export function uniqueEmail(prefix = 'user'): string {
  return `${prefix}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}@example.com`
}

/**
 * Register and log in through the API. `page.request` shares the page's cookie jar, so the
 * page is logged in afterwards. Used when the login screens are not what the test is about.
 */
export async function logIn(page: Page, email = uniqueEmail()): Promise<string> {
  const credentials = { email, password: PASSWORD }
  expect((await page.request.post('/api/v1/auth/register', { data: credentials })).status()).toBe(
    201,
  )
  expect((await page.request.post('/api/v1/auth/login', { data: credentials })).status()).toBe(204)
  return email
}

/** A second, independent user in a separate browser context (own cookies). */
export async function anotherUser(browser: Browser, baseURL: string): Promise<Page> {
  const context = await browser.newContext({ baseURL })
  const page = await context.newPage()
  await logIn(page, uniqueEmail('other'))
  return page
}

/** Light-hearted polls used as test data: they also show up in demos and screenshots. */
export const SAMPLE_POLLS = [
  {
    question: 'Pain au chocolat ou chocolatine ?',
    options: ['Pain au chocolat', 'Chocolatine', 'Je mange les deux'],
  },
  {
    question: "L'ananas sur la pizza, c'est…",
    options: ['Un crime', 'Un délice', "Ça dépend de l'humeur"],
  },
  {
    question: 'Les chaussettes avec des sandales ?',
    options: ['Jamais', 'En vacances seulement', "Toute l'année"],
  },
  {
    question: 'Le dimanche matin, on se lève…',
    options: ['Avant 8 h', 'Vers midi', 'Quel réveil ?'],
  },
  { question: 'Plutôt chat ou chien ?', options: ['Chat', 'Chien', 'Poisson rouge'] },
] as const

export type SamplePoll = (typeof SAMPLE_POLLS)[number]

export function randomPoll(): SamplePoll {
  return SAMPLE_POLLS[Math.floor(Math.random() * SAMPLE_POLLS.length)]
}

export interface CreatedPoll {
  id: string
  question: string
  options: { id: string; label: string }[]
}

/** Create a poll through the API. */
export async function createPoll(
  page: Page,
  poll: SamplePoll = randomPoll(),
): Promise<CreatedPoll> {
  const response = await page.request.post('/api/v1/polls', {
    data: { question: poll.question, options: poll.options },
  })
  expect(response.status()).toBe(201)
  return response.json()
}

export const test = base
export { expect }
