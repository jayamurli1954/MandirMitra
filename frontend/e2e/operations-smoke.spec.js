const { test, expect } = require('@playwright/test');
const { login } = require('./support/auth');
const { getUiProfile } = require('./support/uiProfile');

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
    const ui = getUiProfile();
    await openProtectedPage(page, '/donations');
    await expect(page.getByText(new RegExp(ui.recordDonationButtonName, 'i'))).toBeVisible();
    await expect(page.getByText(new RegExp(ui.recentDonationsText, 'i'))).toBeVisible();

    await openProtectedPage(page, '/sevas');
    await expect(page.getByRole('heading', { name: new RegExp(ui.sevasHeading, 'i') })).toBeVisible();
    await expect(page.getByText(new RegExp(ui.bookingsRescheduleText, 'i'))).toBeVisible();
    await expect(page.getByRole('button', { name: new RegExp(ui.bookNowButtonName, 'i') }).first()).toBeVisible();
  });

  test('loads inventory, HR, reports, panchang, and payment pages', async ({ page }) => {
    const ui = getUiProfile();
    await openProtectedPage(page, '/inventory');
    await expect(page.getByText(/current stock balances/i)).toBeVisible();
    await page.getByRole('tab', { name: new RegExp(ui.itemMasterTabName, 'i') }).click();
    await expect(page.getByText(new RegExp(ui.itemMasterRegisterText, 'i'))).toBeVisible();

    await openProtectedPage(page, '/hr');
    await expect(page.getByText(new RegExp(ui.employeeDirectoryText, 'i'))).toBeVisible();
    await expect(page.getByRole('tab', { name: new RegExp(ui.payrollTabName, 'i') })).toBeVisible();

    await openProtectedPage(page, '/accounting/upi-payments');
    await expect(page.getByRole('heading', { name: new RegExp(ui.upiHeading, 'i') })).toBeVisible();
    await expect(page.getByText(new RegExp(ui.quickLogUpiText, 'i'))).toBeVisible();

    await openProtectedPage(page, '/accounting/reports');
    await expect(page.getByRole('button', { name: new RegExp(ui.generateReportButtonName, 'i') }).first()).toBeVisible();

    await openProtectedPage(page, '/panchang');
    await expect(page.getByRole('heading', { name: new RegExp(ui.panchangHeading, 'i'), exact: true })).toBeVisible();
  });
});

