/**
 * E2E Tests for Seva Booking Flow
 *
 * Tests the complete user journey for booking sevas/poojas
 */

import { test, expect } from '@playwright/test';

test.describe('Seva Booking Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should book a seva successfully', async ({ page }) => {
    // Navigate to seva booking
    await page.click('text=Sevas');
    await expect(page).toHaveURL(/.*sevas/);

    // Click "New Booking"
    await page.click('button:has-text("New Booking")');

    // Select seva
    await page.selectOption('select[name="seva_id"]', { label: /abhishekam/i });

    // Fill devotee details
    await page.fill('input[name="devotee_name"]', 'Krishna Kumar');
    await page.fill('input[name="phone"]', '9876543210');

    // Select date (tomorrow)
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const dateStr = tomorrow.toISOString().split('T')[0];
    await page.fill('input[name="seva_date"]', dateStr);

    // Fill additional details
    await page.selectOption('select[name="gotra"]', 'Bharadwaja');
    await page.selectOption('select[name="nakshatra"]', 'Rohini');

    // Select payment method
    await page.selectOption('select[name="payment_method"]', 'cash');

    // Submit booking
    await page.click('button:has-text("Book")');

    // Verify success
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText(/booking.*success|seva.*booked/i);

    // Verify receipt number generated
    await expect(page.locator('text=/SB-\\d{6}/')).toBeVisible();
  });

  test('should check seva availability before booking', async ({ page }) => {
    await page.click('text=Sevas');

    // Click seva to view details
    await page.click('text=/abhishekam|archana|pooja/i');

    // Check availability calendar
    await expect(page.locator('.availability, .calendar')).toBeVisible();

    // Verify available dates are shown
    await expect(page.locator('.available-slot')).not.toHaveCount(0);
  });

  test('should prevent booking on fully booked date', async ({ page }) => {
    await page.click('text=Sevas');
    await page.click('button:has-text("New Booking")');

    // Try to book on a fully booked date (mocked scenario)
    await page.selectOption('select[name="seva_id"]', { index: 0 });
    await page.fill('input[name="devotee_name"]', 'Test User');
    await page.fill('input[name="seva_date"]', '2024-12-25'); // Assume fully booked

    await page.click('button:has-text("Book")');

    // Should show error about unavailability
    await expect(page.locator('.error-message, .alert-danger')).toContainText(/full|not available|booked/i);
  });

  test('should generate seva booking receipt', async ({ page }) => {
    await page.click('text=Sevas');

    // Find first booking and generate receipt
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Receipt"), a:has-text("Receipt")').first();
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/\.pdf$/);
  });

  test('should cancel a seva booking', async ({ page }) => {
    await page.click('text=Sevas');

    // Find booking and click cancel
    const firstBooking = page.locator('.booking-row, tr').first();
    await firstBooking.locator('button:has-text("Cancel")').click();

    // Confirm cancellation
    await page.fill('textarea[name="reason"]', 'Devotee requested cancellation');
    await page.click('button:has-text("Confirm")');

    // Verify cancellation
    await expect(page.locator('.success-message')).toContainText(/cancel.*success/i);
    await expect(firstBooking).toContainText(/cancelled/i);
  });

  test('should filter bookings by date', async ({ page }) => {
    await page.click('text=Sevas');
    await page.click('text=Bookings');

    // Apply date filter
    await page.fill('input[name="start_date"]', '2024-12-01');
    await page.fill('input[name="end_date"]', '2024-12-31');
    await page.click('button:has-text("Filter")');

    // Verify results
    await expect(page.locator('.booking-row, tr')).not.toHaveCount(0);
  });
});

test.describe('Seva Schedule Management', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should view daily seva schedule', async ({ page }) => {
    await page.click('text=Sevas');
    await page.click('text=Schedule');

    // View today's schedule
    await expect(page.locator('h2, h3')).toContainText(/schedule|today/i);

    // Verify seva listings
    await expect(page.locator('.seva-item, .schedule-item')).not.toHaveCount(0);
  });

  test('should export seva bookings report', async ({ page }) => {
    await page.click('text=Sevas');

    // Click export button
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Export")');
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/\.(xlsx|csv)$/);
  });
});
