/**
 * Tests for the App component (src/App.js)
 * Covers: routing, protected routes, theme, provider wrapping
 */
import React from 'react';
import { render, screen } from '@testing-library/react';
import App from '../App';

// Mock all page components to keep tests fast and focused on routing
jest.mock('../pages/Login', () => () => <div data-testid="login-page">Login Page</div>);
jest.mock('../pages/Dashboard', () => () => <div data-testid="dashboard-page">Dashboard</div>);
jest.mock('../pages/Donations', () => () => <div data-testid="donations-page">Donations</div>);
jest.mock('../pages/Devotees', () => () => <div data-testid="devotees-page">Devotees</div>);
jest.mock('../pages/Reports', () => () => <div data-testid="reports-page">Reports</div>);
jest.mock('../pages/Sevas', () => () => <div data-testid="sevas-page">Sevas</div>);
jest.mock('../pages/SevaManagement', () => () => <div data-testid="seva-management-page">Seva Management</div>);
jest.mock('../pages/Settings', () => () => <div data-testid="settings-page">Settings</div>);
jest.mock('../pages/Panchang', () => () => <div data-testid="panchang-page">Panchang</div>);
jest.mock('../pages/PanchangSettings', () => () => <div data-testid="panchang-settings-page">Panchang Settings</div>);
jest.mock('../pages/CategoryWiseDonationReport', () => () => <div>Cat Report</div>);
jest.mock('../pages/DetailedDonationReport', () => () => <div>Detailed Donation</div>);
jest.mock('../pages/DetailedSevaReport', () => () => <div>Detailed Seva</div>);
jest.mock('../pages/SevaSchedule', () => () => <div>Seva Schedule</div>);
jest.mock('../pages/SevaRescheduleApproval', () => () => <div>Reschedule Approval</div>);
jest.mock('../pages/accounting/ChartOfAccounts', () => () => <div>COA</div>);
jest.mock('../pages/accounting/QuickExpense', () => () => <div>Quick Expense</div>);
jest.mock('../pages/accounting/JournalEntries', () => () => <div>Journal Entries</div>);
jest.mock('../pages/accounting/UpiPayments', () => () => <div>UPI Payments</div>);
jest.mock('../pages/accounting/AccountingReports', () => () => <div>Accounting Reports</div>);

// Helper to render App with a specific URL
const renderAppAt = (url) => {
    window.history.pushState({}, 'Test', url);
    return render(<App />);
};

beforeEach(() => {
    localStorage.clear();
});

describe('App - Routing', () => {
    it('renders Login page at /login', () => {
        renderAppAt('/login');
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    it('redirects to /login when accessing /dashboard without token', () => {
        renderAppAt('/dashboard');
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });

    it('renders Dashboard when authenticated and accessing /dashboard', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/dashboard');
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    it('renders Devotees page when authenticated and accessing /devotees', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/devotees');
        expect(screen.getByTestId('devotees-page')).toBeInTheDocument();
    });

    it('renders Donations page when authenticated and accessing /donations', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/donations');
        expect(screen.getByTestId('donations-page')).toBeInTheDocument();
    });

    it('renders Sevas page when authenticated and accessing /sevas', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/sevas');
        expect(screen.getByTestId('sevas-page')).toBeInTheDocument();
    });

    it('renders SevaManagement page at /sevas/manage', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/sevas/manage');
        expect(screen.getByTestId('seva-management-page')).toBeInTheDocument();
    });

    it('renders Settings page at /settings', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/settings');
        expect(screen.getByTestId('settings-page')).toBeInTheDocument();
    });

    it('renders Panchang page at /panchang', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/panchang');
        expect(screen.getByTestId('panchang-page')).toBeInTheDocument();
    });

    it('redirects to /dashboard from / when authenticated', () => {
        localStorage.setItem('token', 'valid-token');
        renderAppAt('/');
        expect(screen.getByTestId('dashboard-page')).toBeInTheDocument();
    });

    it('redirects to /login from / when not authenticated', () => {
        renderAppAt('/');
        expect(screen.getByTestId('login-page')).toBeInTheDocument();
    });
});

describe('App - Theme', () => {
    it('renders without crashing', () => {
        expect(() => renderAppAt('/login')).not.toThrow();
    });
});
