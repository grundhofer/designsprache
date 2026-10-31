// Rendered browser regression checks for the generated site in docs/.
// Run `python3 build.py` in the repository root first; the web server below
// only serves what the build produced.
const path = require('node:path');
const { defineConfig, devices } = require('@playwright/test');

const PORT = Number(process.env.BROWSER_TEST_PORT || 8765);
const DOCS = path.resolve(__dirname, '..', '..', 'docs');

module.exports = defineConfig({
  testDir: __dirname,
  testMatch: /.*\.spec\.cjs$/,
  timeout: 90_000,
  expect: { timeout: 10_000 },
  fullyParallel: true,
  workers: process.env.CI ? 2 : undefined,
  forbidOnly: !!process.env.CI,
  retries: 0,
  reporter: process.env.CI ? [['list'], ['github']] : 'list',
  use: {
    ...devices['Desktop Chrome'],
    baseURL: `http://127.0.0.1:${PORT}`,
    locale: 'en-US',
    serviceWorkers: 'block',
    trace: 'retain-on-failure',
  },
  webServer: {
    command: `python3 -m http.server ${PORT} --bind 127.0.0.1 --directory "${DOCS}"`,
    url: `http://127.0.0.1:${PORT}/en/`,
    reuseExistingServer: !process.env.CI,
    stdout: 'ignore',
    stderr: 'ignore',
    timeout: 30_000,
  },
});
