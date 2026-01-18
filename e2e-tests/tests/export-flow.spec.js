// @ts-check
const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('Accounting Exports Verification', () => {
    let authToken;

    test.beforeAll(async ({ request }) => {
        // 1. Login to get token
        const loginResponse = await request.post('/api/v1/login/access-token', {
            form: {
                username: 'admin@MandirMitra.com', // Adjust based on seed data
                password: 'password' // Adjust based on seed data
            }
        });

        // Allow for 401 if seed data is different, but try standard creds
        if (loginResponse.ok()) {
            const data = await loginResponse.json();
            authToken = data.access_token;
        } else {
            console.log('Login failed, tests might fail if auth is required');
        }
    });

    // Helper to download file
    const downloadFile = async (request, url, expectedType) => {
        const response = await request.get(url, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });

        expect(response.status()).toBe(200);

        const contentType = response.headers()['content-type'];
        if (expectedType === 'excel') {
            expect(contentType).toContain('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet');
        } else if (expectedType === 'pdf') {
            expect(contentType).toBe('application/pdf');
        }

        const body = await response.body();
        expect(body.length).toBeGreaterThan(0);

        return body;
    };

    test('Day Book Export Excel', async ({ request }) => {
        const today = new Date().toISOString().split('T')[0];
        await downloadFile(request, `/api/v1/journal-entries/reports/day-book/export/excel?date=${today}`, 'excel');
    });

    test('Day Book Export PDF', async ({ request }) => {
        const today = new Date().toISOString().split('T')[0];
        await downloadFile(request, `/api/v1/journal-entries/reports/day-book/export/pdf?date=${today}`, 'pdf');
    });

    test('Cash Book Export Excel', async ({ request }) => {
        const today = new Date().toISOString().split('T')[0];
        // Using a wide date range to ensure some data
        await downloadFile(request, `/api/v1/journal-entries/reports/cash-book/export/excel?from_date=2024-01-01&to_date=${today}`, 'excel');
    });

    test('Cash Book Export PDF', async ({ request }) => {
        const today = new Date().toISOString().split('T')[0];
        await downloadFile(request, `/api/v1/journal-entries/reports/cash-book/export/pdf?from_date=2024-01-01&to_date=${today}`, 'pdf');
    });

    // Bank Book requires an account ID. We need to fetch accounts first.
    test('Bank Book Export Verification', async ({ request }) => {
        // Get Accounts to find a bank account
        const accountsRes = await request.get('/api/v1/accounts', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });

        let bankAccountId = 1; // Default fallback
        if (accountsRes.ok()) {
            const accounts = await accountsRes.json();
            // Look for asset account, subtype cash_bank (usually subtype 2 or code starting with 11)
            // Adjust logic based on your seed data structure
            const bankAccount = accounts.find(a => a.account_code && a.account_code.startsWith('111'));
            if (bankAccount) {
                bankAccountId = bankAccount.id;
            }
        }

        const today = new Date().toISOString().split('T')[0];

        // Excel
        await downloadFile(request, `/api/v1/journal-entries/reports/bank-book/export/excel?account_id=${bankAccountId}&from_date=2024-01-01&to_date=${today}`, 'excel');

        // PDF
        await downloadFile(request, `/api/v1/journal-entries/reports/bank-book/export/pdf?account_id=${bankAccountId}&from_date=2024-01-01&to_date=${today}`, 'pdf');
    });
});
