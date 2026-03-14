const { test, expect } = require('@playwright/test');
const { login } = require('./support/auth');

test.describe('Authentication and dashboard', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    await page.goto('/dashboard');
    await page.waitForURL(/\/login/, { timeout: 15000 });
    await expect(page.getByLabel(/email address/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /sign in/i })).toBeVisible();
  });

  test('logs in and shows the main dashboard widgets', async ({ page }) => {
    await login(page);
    await expect(page.getByText(/quick donation entry/i)).toBeVisible();
    await expect(page.getByText(/today's panchang/i)).toBeVisible();
    await expect(page.getByText(/donations/i).first()).toBeVisible();
    await expect(page.getByText(/sevas/i).first()).toBeVisible();
  });
});
