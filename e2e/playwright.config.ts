import { defineConfig, devices } from '@playwright/test'

const isCI = Boolean(process.env.CI)
// Delay between actions, set by `npm run test:headed` so a human can follow the test.
const slowMo = Number(process.env.SLOW_MO ?? 0)

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  // A forgotten test.only must never silently skip the rest of the suite in CI.
  forbidOnly: isCI,
  retries: isCI ? 1 : 0,
  // Slowed-down runs need more time than the default 30 s per test.
  timeout: slowMo > 0 ? 180_000 : 30_000,
  reporter: isCI
    ? [['list'], ['html', { open: 'never' }], ['junit', { outputFile: 'test-results/junit.xml' }]]
    : [['list'], ['html', { open: 'never' }]],
  use: {
    // The disposable stack started with `npm run stack:up` (never the development stack).
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:8081',
    trace: 'retain-on-failure',
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    launchOptions: { slowMo },
  },
  projects: [
    { name: 'desktop', use: { ...devices['Desktop Chrome'] } },
    { name: 'mobile', use: { ...devices['Pixel 7'] } },
  ],
})
