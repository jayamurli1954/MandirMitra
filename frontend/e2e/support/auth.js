const { expect } = require('@playwright/test');

function requireEnv(name) {
  const value = process.env[name];
  if (!value) {
    throw new Error(`Missing required environment variable: ${name}`);
  }
  return value;
}

async function login(page) {
  const username = requireEnv('PLAYWRIGHT_TEST_USERNAME');
  const password = requireEnv('PLAYWRIGHT_TEST_PASSWORD');

  await page.goto('/login');
  await expect(page.getByLabel(/email address/i)).toBeVisible();
  await page.getByLabel(/email address/i).fill(username);
  await page.locator('#password').fill(password);
  await page.getByRole('button', { name: /sign in/i }).click();

  await page.waitForURL(/\/brand-intro|\/dashboard|\/setup-wizard/, { timeout: 30000 });

  if (page.url().includes('/brand-intro')) {
    await page.getByRole('button', { name: /continue/i }).click();
  }

  await page.waitForURL(/\/dashboard|\/setup-wizard/, { timeout: 30000 });

  if (page.url().includes('/setup-wizard')) {
    throw new Error('Login landed on /setup-wizard. Finish onboarding or use an already-onboarded test account for Playwright E2E runs.');
  }

  await expect(page).toHaveURL(/\/dashboard/);
  await expect(page.getByRole('heading', { name: /dashboard/i })).toBeVisible();
}

module.exports = { login };


