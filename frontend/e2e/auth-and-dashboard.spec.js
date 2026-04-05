const { test, expect } = require('@playwright/test');
const { login } = require('./support/auth');
const { getUiProfile } = require('./support/uiProfile');

test.describe('Authentication and dashboard', () => {
  test('redirects unauthenticated users to login', async ({ page }) => {
    const ui = getUiProfile();
    await page.goto('/dashboard');
    await page.waitForURL(/\/login/, { timeout: 15000 });
    await expect(page.getByLabel(new RegExp(ui.loginEmailLabel, 'i'))).toBeVisible();
    await expect(page.getByRole('button', { name: new RegExp(ui.loginButtonName, 'i') })).toBeVisible();
  });

  test('logs in and shows the main dashboard widgets', async ({ page }) => {
    const ui = getUiProfile();
    await login(page);
    await expect(page.getByText(new RegExp(ui.quickDonationHeading, 'i'))).toBeVisible();
    await expect(page.getByText(new RegExp(ui.panchangHeading, 'i'))).toBeVisible();
    await expect(page.getByText(new RegExp(ui.donationsHeading, 'i')).first()).toBeVisible();
    await expect(page.getByText(new RegExp(ui.sevasHeading, 'i')).first()).toBeVisible();
  });
});
