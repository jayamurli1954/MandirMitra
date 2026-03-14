const { defineConfig, devices } = require('@playwright/test');

const baseURL = process.env.PLAYWRIGHT_BASE_URL || 'http://localhost:3000';
const backendURL = process.env.PLAYWRIGHT_BACKEND_URL || 'http://127.0.0.1:8000';
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER === '1';

module.exports = defineConfig({
  testDir: './e2e',
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [['list'], ['html', { open: 'never' }]],
  timeout: 90 * 1000,
  expect: {
    timeout: 15 * 1000,
  },
  use: {
    baseURL,
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    viewport: { width: 1440, height: 960 },
  },
  webServer: skipWebServer
    ? undefined
    : [
        {
          command: 'python -m uvicorn app.main:app --host 127.0.0.1 --port 8000',
          url: backendURL,
          cwd: '../backend',
          timeout: 180 * 1000,
          reuseExistingServer: !process.env.CI,
          env: {
            ...process.env,
          },
        },
        {
          command: 'npm run start:e2e',
          url: baseURL,
          timeout: 180 * 1000,
          reuseExistingServer: !process.env.CI,
          env: {
            ...process.env,
            BROWSER: 'none',
            REACT_APP_API_URL: backendURL,
            REACT_APP_FALLBACK_API_URL: backendURL,
          },
        },
      ],
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});

