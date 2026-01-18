/**
 * E2E Tests for Donation Flow
 *
 * Tests the complete user journey for recording donations
 */

import { test, expect } from '@playwright/test';

test.describe('Donation Recording Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to application
    await page.goto('/');

    // Login (adjust selectors based on your app)
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');

    // Wait for dashboard to load
    await page.waitForURL('**/dashboard');
  });

  test('should record a cash donation successfully', async ({ page }) => {
    // Navigate to donations page
    await page.click('text=Donations');
    await expect(page).toHaveURL(/.*donations/);

    // Click "Add New Donation" button
    await page.click('button:has-text("New Donation")');

    // Fill donation form
    await page.fill('input[name="donor_name"]', 'Ram Kumar');
    await page.fill('input[name="amount"]', '1000');
    await page.selectOption('select[name="payment_method"]', 'cash');
    await page.fill('input[name="phone"]', '9876543210');
    await page.fill('textarea[name="purpose"]', 'Temple development');

    // Submit form
    await page.click('button:has-text("Save")');

    // Verify success message
    await expect(page.locator('.success-message, .alert-success')).toBeVisible();
    await expect(page.locator('.success-message, .alert-success')).toContainText(/donation.*recorded|success/i);

    // Verify donation appears in list
    await expect(page.locator('text=Ram Kumar')).toBeVisible();
    await expect(page.locator('text=₹1,000')).toBeVisible();
  });

  test('should generate donation receipt PDF', async ({ page }) => {
    // Navigate to donations
    await page.click('text=Donations');

    // Find first donation and click receipt button
    const firstDonation = page.locator('tr').first();
    const receiptButton = firstDonation.locator('button:has-text("Receipt")');

    // Listen for download
    const downloadPromise = page.waitForEvent('download');
    await receiptButton.click();
    const download = await downloadPromise;

    // Verify it's a PDF
    expect(download.suggestedFilename()).toMatch(/\.pdf$/);
  });

  test('should record UPI donation with transaction ID', async ({ page }) => {
    await page.click('text=Donations');
    await page.click('button:has-text("New Donation")');

    // Fill UPI donation
    await page.fill('input[name="donor_name"]', 'Sita Sharma');
    await page.fill('input[name="amount"]', '5000');
    await page.selectOption('select[name="payment_method"]', 'upi');
    await page.fill('input[name="transaction_id"]', 'UPI123456789');
    await page.fill('input[name="email"]', 'sita@example.com');

    await page.click('button:has-text("Save")');

    // Verify success
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('text=UPI123456789')).toBeVisible();
  });

  test('should validate required fields', async ({ page }) => {
    await page.click('text=Donations');
    await page.click('button:has-text("New Donation")');

    // Try to submit without filling required fields
    await page.click('button:has-text("Save")');

    // Verify validation errors appear
    await expect(page.locator('.error, .invalid-feedback')).toBeVisible();
  });

  test('should filter donations by date', async ({ page }) => {
    await page.click('text=Donations');

    // Set date filter
    await page.fill('input[name="start_date"]', '2024-12-01');
    await page.fill('input[name="end_date"]', '2024-12-31');
    await page.click('button:has-text("Filter")');

    // Verify filtered results
    await expect(page.locator('.donation-row, tr')).not.toHaveCount(0);
  });

  test('should search donations by donor name', async ({ page }) => {
    await page.click('text=Donations');

    // Enter search term
    await page.fill('input[placeholder*="Search"], input[name="search"]', 'Kumar');
    await page.waitForTimeout(500); // Debounce

    // Verify search results
    await expect(page.locator('text=Kumar')).toBeVisible();
  });
});

test.describe('80G Certificate Generation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should generate 80G certificate for eligible donation', async ({ page }) => {
    await page.click('text=Donations');
    await page.click('button:has-text("New Donation")');

    // Create 80G eligible donation
    await page.fill('input[name="donor_name"]', 'Taxpayer Name');
    await page.fill('input[name="amount"]', '10000');
    await page.fill('input[name="pan_number"]', 'ABCDE1234F');
    await page.check('input[name="is_80g_eligible"]');
    await page.selectOption('select[name="payment_method"]', 'bank_transfer');

    await page.click('button:has-text("Save")');

    // Generate 80G certificate
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("80G Certificate")');
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/80g.*\.pdf$/i);
  });
});
