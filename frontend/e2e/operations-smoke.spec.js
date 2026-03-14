const { test, expect } = require('@playwright/test');
const { login } = require('./support/auth');

async function openProtectedPage(page, path) {
  await page.goto(path);
  const escapedPath = path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  await expect(page).toHaveURL(new RegExp(`${escapedPath}(?:$|[?#])`));
}

test.describe('Operational page smoke checks', () => {
  test.beforeEach(async ({ page }) => {
    await login(page);
  });

  test('loads donation and seva workflows', async ({ page }) => {
    await openProtectedPage(page, '/donations');
    await expect(page.getByText(/record donations/i)).toBeVisible();
    await expect(page.getByText(/recent donations/i)).toBeVisible();

    await openProtectedPage(page, '/sevas');
    await expect(page.getByRole('heading', { name: /sevas/i })).toBeVisible();
    await expect(page.getByText(/bookings \/ reschedule/i)).toBeVisible();
    await expect(page.getByRole('button', { name: /book now/i }).first()).toBeVisible();
  });

  test('loads inventory, HR, reports, panchang, and payment pages', async ({ page }) => {
    await openProtectedPage(page, '/inventory');
    await expect(page.getByText(/current stock balances/i)).toBeVisible();
    await page.getByRole('tab', { name: /item master/i }).click();
    await expect(page.getByText(/item master register/i)).toBeVisible();

    await openProtectedPage(page, '/hr');
    await expect(page.getByText(/employee & priest directory/i)).toBeVisible();
    await expect(page.getByRole('tab', { name: /payroll & salaries/i })).toBeVisible();

    await openProtectedPage(page, '/accounting/upi-payments');
    await expect(page.getByRole('heading', { name: /upi payment logging/i })).toBeVisible();
    await expect(page.getByText(/quick log upi payment/i)).toBeVisible();

    await openProtectedPage(page, '/accounting/reports');
    await expect(page.getByRole('button', { name: /generate report/i }).first()).toBeVisible();

    await openProtectedPage(page, '/panchang');
    await expect(page.getByRole('heading', { name: "Today's Panchang", exact: true })).toBeVisible();
  });
});

