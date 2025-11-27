/**
 * E2E Tests for HR Management Flow
 *
 * Tests employee management and payroll processing
 */

import { test, expect } from '@playwright/test';

test.describe('Employee Management Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should create a new employee', async ({ page }) => {
    // Navigate to HR
    await page.click('text=HR');
    await page.click('text=Employees');

    // Click "Add Employee"
    await page.click('button:has-text("Add Employee")');

    // Fill employee details
    await page.fill('input[name="full_name"]', 'Rajesh Kumar');
    await page.fill('input[name="phone"]', '9876543210');
    await page.fill('input[name="email"]', 'rajesh@temple.org');
    await page.fill('input[name="date_of_birth"]', '1990-01-15');
    await page.selectOption('select[name="gender"]', 'male');

    // Employment details
    await page.fill('input[name="joining_date"]', '2024-01-01');
    await page.selectOption('select[name="employee_type"]', 'permanent');
    await page.fill('input[name="basic_salary"]', '25000');

    // Submit
    await page.click('button:has-text("Save")');

    // Verify success
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('text=Rajesh Kumar')).toBeVisible();
  });

  test('should view employee details', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Employees');

    // Click first employee
    await page.click('.employee-row, tr').first();

    // Verify details page loaded
    await expect(page.locator('h2, h3')).toContainText(/employee.*details|profile/i);
    await expect(page.locator('text=/emp-\\d{4}/i')).toBeVisible(); // Employee code
  });

  test('should filter employees by department', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Employees');

    // Select department filter
    await page.selectOption('select[name="department"]', { index: 1 });

    // Verify filtered results
    await expect(page.locator('.employee-row, tr')).not.toHaveCount(0);
  });
});

test.describe('Payroll Processing Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    await page.waitForURL('**/dashboard');
  });

  test('should generate monthly payroll', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Payroll');

    // Click "Generate Payroll"
    await page.click('button:has-text("Generate")');

    // Select month and year
    await page.selectOption('select[name="month"]', 'December');
    await page.selectOption('select[name="year"]', '2024');

    // Confirm generation
    await page.click('button:has-text("Generate")');

    // Wait for processing
    await expect(page.locator('.success-message')).toBeVisible({ timeout: 10000 });
    await expect(page.locator('.success-message')).toContainText(/payroll.*generated/i);
  });

  test('should view payslip', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Payroll');

    // View first payslip
    const downloadPromise = page.waitForEvent('download');
    await page.click('button:has-text("Payslip"), a:has-text("Payslip")').first();
    const download = await downloadPromise;

    expect(download.suggestedFilename()).toMatch(/payslip.*\.pdf$/i);
  });

  test('should approve payroll', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Payroll');

    // Find draft payroll
    const draftRow = page.locator('text=Draft').locator('..').locator('..');
    await draftRow.locator('button:has-text("Approve")').click();

    // Confirm approval
    await page.click('button:has-text("Confirm")');

    // Verify approved
    await expect(page.locator('.success-message')).toContainText(/approved/i);
    await expect(draftRow).toContainText(/approved/i);
  });

  test('should filter payroll by month', async ({ page }) => {
    await page.click('text=HR');
    await page.click('text=Payroll');

    // Select month
    await page.selectOption('select[name="month"]', 'December');
    await page.selectOption('select[name="year"]', '2024');
    await page.click('button:has-text("Filter")');

    // Verify results
    await expect(page.locator('.payroll-row, tr')).not.toHaveCount(0);
  });
});
