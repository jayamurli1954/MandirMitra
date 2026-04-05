const { test, expect } = require('@playwright/test');
const { login } = require('./support/auth');
const { getUiProfile } = require('./support/uiProfile');

function escapeRegex(value) {
  return String(value).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function parseAmount(text) {
  const match = String(text).match(/-?[\d,]+(?:\.\d+)?/);
  if (!match) {
    return 0;
  }
  return Number(match[0].replace(/,/g, ''));
}

function parseDashboardCard(text) {
  const lines = String(text)
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  const amountLine = lines.find((line) => /\d/.test(line)) || '0';
  const countLine = lines.find((line) => /(donations|bookings)/i.test(line)) || '0';

  return {
    amount: parseAmount(amountLine),
    count: Number((countLine.match(/\d+/) || ['0'])[0]),
  };
}

async function openProtectedPage(page, path) {
  await page.goto(path);
  const escapedPath = path.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  await expect(page).toHaveURL(new RegExp(`${escapedPath}(?:$|[?#])`));
}

function activeTabPanel(page) {
  return page.locator('[role="tabpanel"]:not([hidden])').first();
}

async function openSelect(scope, labelRegex) {
  const combo = scope.getByRole('combobox', { name: labelRegex });
  if (await combo.count()) {
    await combo.first().click();
    return;
  }

  const labeled = scope.getByLabel(labelRegex);
  await labeled.first().click();
}

async function selectMuiOption(page, scope, labelRegex, optionText) {
  await openSelect(scope, labelRegex);
  await page.getByRole('option', { name: new RegExp(`^${escapeRegex(optionText)}$`) }).click();
}

async function selectFirstAccount(page, scope, labelRegex) {
  await openSelect(scope, labelRegex);
  const option = page.getByRole('option').filter({ hasText: / - / }).first();
  await expect(option).toBeVisible();
  const label = (await option.innerText()).trim();
  await option.click();
  return label;
}

async function selectBookingDialogCashAccount(page, bookingDialog, optionText) {
  const cashAccountSelect = bookingDialog.getByRole('combobox').nth(1);
  await cashAccountSelect.click();

  let option = page.getByRole('option').filter({ hasText: / - / }).first();
  if (optionText) {
    option = page.getByRole('option', { name: new RegExp(`^${escapeRegex(optionText)}$`) });
  }

  await expect(option).toBeVisible();
  const label = (await option.first().innerText()).trim();
  await option.first().click();
  return label;
}

async function waitForPdfResponse(page, urlRegex, trigger) {
  const responsePromise = page.waitForResponse((response) => {
    return urlRegex.test(response.url()) && response.request().method() === 'GET';
  });

  await trigger();
  const response = await responsePromise;
  expect(response.ok()).toBeTruthy();

  const contentType = ((await response.headerValue('content-type')) || '').toLowerCase();
  expect(contentType).toContain('application/pdf');
  return response;
}

async function readDashboardCardByTitle(page, title, index = 0) {
  const titleLocator = page.getByText(title, { exact: true }).nth(index);
  await expect(titleLocator).toBeVisible();
  const card = titleLocator.locator('xpath=ancestor::*[contains(@class,"MuiCard-root")][1]');
  const text = await card.innerText();
  return parseDashboardCard(text);
}

async function getDashboardSnapshot(page) {
  return {
    donationToday: await readDashboardCardByTitle(page, "Today's Donation"),
    donationMonth: await readDashboardCardByTitle(page, 'Cumulative for Month', 0),
    sevaToday: await readDashboardCardByTitle(page, "Today's Seva"),
    sevaMonth: await readDashboardCardByTitle(page, 'Cumulative for Month', 1),
  };
}

async function getTrialBalanceTotals(page) {
  await openProtectedPage(page, '/accounting/reports');
  const panel = activeTabPanel(page);
  const ui = getUiProfile();
  await panel.getByRole('button', { name: new RegExp(ui.generateReportButtonName, 'i') }).click();
  await expect(panel.getByText(/trial balance as of/i)).toBeVisible();

  const totalRow = panel.getByRole('row').filter({ hasText: /^TOTAL/ }).last();
  await expect(totalRow).toBeVisible();
  const text = await totalRow.innerText();
  const amounts = text.match(/-?[\d,]+\.\d{2}/g) || [];

  if (amounts.length < 2) {
    throw new Error(`Could not parse trial balance totals from row: ${text}`);
  }

  return {
    debit: Number(amounts[0].replace(/,/g, '')),
    credit: Number(amounts[1].replace(/,/g, '')),
  };
}

async function ensureDevoteeInBookingDialog(page, bookingDialog, phone, firstName, lastName) {
  const ui = getUiProfile();
  await expect(bookingDialog.getByText(/step 1: enter devotee mobile number/i)).toBeVisible();
  await bookingDialog.getByLabel(new RegExp(ui.mobileNumberLabel, 'i')).fill(phone);
  await bookingDialog.getByRole('button', { name: new RegExp(ui.searchButtonName, 'i') }).click();

  await expect
    .poll(async () => {
      const foundVisible = await bookingDialog.getByText(/devotee found!/i).isVisible().catch(() => false);
      const createVisible = await bookingDialog.getByLabel(/first name/i).isVisible().catch(() => false);
      return foundVisible ? 'found' : createVisible ? 'create' : '';
    })
    .toMatch(/found|create/);

  const needsCreate = await bookingDialog.getByLabel(/first name/i).isVisible().catch(() => false);
  if (needsCreate) {
    await bookingDialog.getByLabel(/first name/i).fill(firstName);
    await bookingDialog.getByLabel(/^last name$/i).fill(lastName);
    await bookingDialog.getByRole('button', { name: new RegExp(ui.createContinueButtonName, 'i') }).click();
  }

  await expect(bookingDialog.getByText(/devotee found!/i)).toBeVisible();
  await expect(bookingDialog.getByText(/step 2: seva booking details/i)).toBeVisible();
}

async function getAvailableSevaCard(page) {
  const ui = getUiProfile();
  return page
    .getByText(/^Available Today$/)
    .first()
    .locator(`xpath=ancestor::*[.//button[normalize-space()="${ui.bookNowButtonName}"]][1]`);
}

async function getUnavailableSevaCard(page) {
  const ui = getUiProfile();
  return page
    .getByText(/^Not Available Today$/)
    .first()
    .locator(`xpath=ancestor::*[.//button[normalize-space()="${ui.bookNowButtonName}"]][1]`);
}

test.describe('Transactional E2E coverage', () => {
  test('creates donation and seva booking, downloads receipts, updates dashboard totals, and posts accounting entries', async ({ page }) => {
    test.setTimeout(180000);

    const uniqueSuffix = String(Date.now()).slice(-5);
    const firstName = `PW${uniqueSuffix}`;
    const lastName = 'Txn';
    const donationAmount = 5100 + (Date.now() % 200);
    const sevaAmount = 6200 + (Date.now() % 200);
    const uniquePhone = `9${String(Date.now()).slice(-9)}`;
    const today = new Date().toISOString().split('T')[0];
    const ui = getUiProfile();

    await login(page);

    const trialBalanceBefore = await getTrialBalanceTotals(page);

    await openProtectedPage(page, '/dashboard');
    await expect(page.getByRole('heading', { name: new RegExp(ui.dashboardHeading, 'i') })).toBeVisible();
    const dashboardBefore = await getDashboardSnapshot(page);

    await page.getByLabel(/phone number/i).fill(uniquePhone);
    await page.getByRole('button', { name: /search mobile/i }).click();
    await expect(page.getByText(/no devotee found for this mobile number/i)).toBeVisible();

    await page.getByLabel(/first name/i).fill(firstName);
    await page.getByLabel(/last name/i).fill(lastName);
    await page.getByLabel(/amount/i).fill(String(donationAmount));
    await selectMuiOption(page, page, /category/i, 'General Donation');
    const cashAccountLabel = await selectFirstAccount(page, page, /cash account code/i);

    await page.getByRole('button', { name: /record donation/i }).click();
    await expect(page.getByText(/donation recorded successfully!/i)).toBeVisible();

    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Donation")).amount).toBe(
      dashboardBefore.donationToday.amount + donationAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Donation")).count).toBe(
      dashboardBefore.donationToday.count + 1
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 0)).amount).toBe(
      dashboardBefore.donationMonth.amount + donationAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 0)).count).toBe(
      dashboardBefore.donationMonth.count + 1
    );

    await openProtectedPage(page, '/donations');
    const donationRow = page.getByRole('row').filter({ hasText: firstName }).first();
    await expect(donationRow).toBeVisible();
    await waitForPdfResponse(page, /\/api\/v1\/donations\/\d+\/receipt\/pdf$/, async () => {
      await donationRow.locator('[title="Download Receipt"]').click();
    });

    await openProtectedPage(page, '/sevas');
    await expect(page.getByRole('heading', { name: new RegExp(ui.sevasHeading, 'i') })).toBeVisible();
    const availableSevaCard = await getAvailableSevaCard(page);
    await availableSevaCard.getByRole('button', { name: new RegExp(ui.bookNowButtonName, 'i') }).click();

    const bookingDialog = page.getByRole('dialog');
    await ensureDevoteeInBookingDialog(page, bookingDialog, uniquePhone, firstName, lastName);

    await bookingDialog.getByLabel(/^amount/i).fill(String(sevaAmount));
    await selectBookingDialogCashAccount(page, bookingDialog, cashAccountLabel);

    await bookingDialog.getByRole('button', { name: /confirm booking/i }).click();
    await expect(bookingDialog.getByText(/seva booked successfully!/i)).toBeVisible();
    await waitForPdfResponse(page, /\/api\/v1\/sevas\/bookings\/\d+\/receipt\/pdf$/, async () => {
      await bookingDialog.getByRole('button', { name: /download receipt/i }).click();
    });
    await expect(bookingDialog).toBeHidden({ timeout: 7000 });

    await openProtectedPage(page, '/dashboard');
    await expect(page.getByRole('heading', { name: new RegExp(ui.dashboardHeading, 'i') })).toBeVisible();

    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Donation")).amount).toBe(
      dashboardBefore.donationToday.amount + donationAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Donation")).count).toBe(
      dashboardBefore.donationToday.count + 1
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 0)).amount).toBe(
      dashboardBefore.donationMonth.amount + donationAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 0)).count).toBe(
      dashboardBefore.donationMonth.count + 1
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Seva")).amount).toBe(
      dashboardBefore.sevaToday.amount + sevaAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, "Today's Seva")).count).toBe(
      dashboardBefore.sevaToday.count + 1
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 1)).amount).toBe(
      dashboardBefore.sevaMonth.amount + sevaAmount
    );
    await expect.poll(async () => (await readDashboardCardByTitle(page, 'Cumulative for Month', 1)).count).toBe(
      dashboardBefore.sevaMonth.count + 1
    );

    const trialBalanceAfter = await getTrialBalanceTotals(page);
    const totalIncrease = donationAmount + sevaAmount;
    expect(trialBalanceAfter.debit).toBeCloseTo(trialBalanceBefore.debit + totalIncrease, 2);
    expect(trialBalanceAfter.credit).toBeCloseTo(trialBalanceBefore.credit + totalIncrease, 2);

    await page.getByRole('tab', { name: new RegExp(ui.accountLedgerTabName, 'i') }).click();
    const ledgerPanel = activeTabPanel(page);
    const ledgerAccountSelect = ledgerPanel.getByRole('combobox').first();
    await ledgerAccountSelect.click();
    await page.getByRole('option', { name: new RegExp(`^${escapeRegex(cashAccountLabel)}$`) }).click();
    await ledgerPanel.getByLabel(/^from date$/i).fill(today);
    await ledgerPanel.getByLabel(/^to date$/i).fill(today);
    await ledgerPanel.getByRole('button', { name: new RegExp(ui.viewLedgerButtonName, 'i') }).click();

    await expect(ledgerPanel.getByText(/opening balance/i)).toBeVisible();
    await expect(ledgerPanel.getByText(new RegExp(`^${escapeRegex(donationAmount.toFixed(2))}$`)).first()).toBeVisible();
    await expect(ledgerPanel.getByText(new RegExp(`^${escapeRegex(sevaAmount.toFixed(2))}$`)).first()).toBeVisible();
    await expect(ledgerPanel.getByText(/closing balance/i)).toBeVisible();
  });

  test('blocks booking for an unavailable Seva and shows the validation error', async ({ page }) => {
    test.setTimeout(120000);

    const uniqueSuffix = String(Date.now()).slice(-5);
    const firstName = `PWB${uniqueSuffix}`;
    const lastName = 'Blocked';
    const uniquePhone = `8${String(Date.now()).slice(-9)}`;
    const ui = getUiProfile();

    await login(page);
    await openProtectedPage(page, '/sevas');
    await expect(page.getByRole('heading', { name: new RegExp(ui.sevasHeading, 'i') })).toBeVisible();

    const unavailableSevaCard = await getUnavailableSevaCard(page);
    await unavailableSevaCard.getByRole('button', { name: new RegExp(ui.bookNowButtonName, 'i') }).click();

    const bookingDialog = page.getByRole('dialog');
    await expect(bookingDialog.getByText(/not available today/i)).toBeVisible();
    await ensureDevoteeInBookingDialog(page, bookingDialog, uniquePhone, firstName, lastName);
    await selectBookingDialogCashAccount(page, bookingDialog);

    await bookingDialog.getByRole('button', { name: /confirm booking/i }).click();
    await expect(
      bookingDialog.getByText(/no slots available for this date|seva not available on/i)
    ).toBeVisible();
  });
});
